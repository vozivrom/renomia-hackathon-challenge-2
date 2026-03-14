"""
Document classifier for Czech insurance documents.

Priority order (lowest → highest):
  VPP → ZPP → DPP → SUR → PS → DOL

Strategy: normalize text → check rules → exactly 1 match = label, 0 or 2+ = ask Gemini
"""

import json
import re
import unicodedata
from typing import Optional

from gemini import gemini

from domain import *

def normalize_text(text: str) -> str:
    """Lowercase + remove diacritics."""
    text = text.lower()
    text = unicodedata.normalize('NFD', text)
    text = ''.join(ch for ch in text if unicodedata.category(ch) != 'Mn')
    return text


def _matches_any(text: str, patterns: list[str]) -> bool:
    return any(re.search(p, text) for p in patterns)


def _find_earliest(text: str) -> Optional[str]:
    """For each doc type that matches, find its earliest match position.
    Return the doc type whose match starts closest to text beginning, or None."""
    best_type = None
    best_pos = len(text) + 1
    for doc_type, patterns in RULES.items():
        for p in patterns:
            m = re.search(p, text)
            if m and m.start() < best_pos:
                best_pos = m.start()
                best_type = doc_type
    return best_type


def _extract_amendment_number(filename: str, ocr_text: str) -> Optional[int]:
    fn = normalize_text(filename)
    tx = normalize_text(ocr_text[:3000]) if ocr_text else ""

    m = re.search(r'\bd(\d+)[\-_]k[\-_]ps', fn)
    if m:
        return int(m.group(1))

    m = re.search(r'(?:kalkulacni\s+)?dodatek\s+c\.\s*(\d+)', tx)
    if m:
        return int(m.group(1))

    m = re.search(r'nalezitosti\s+dodatku\s+c\.\s*(\d+)', tx)
    if m:
        return int(m.group(1))

    return None


def _extract_dolozka_code(filename: str, ocr_text: str) -> Optional[str]:
    combined = normalize_text(f"{filename}\n{ocr_text[:3000]}")

    m = re.search(r'dolozka\s+((?:pp|dop)\s*\d+)', combined)
    if m:
        return m.group(1).upper()

    m = re.search(r'dolozka\s+c\.\s*(\d+)', combined)
    if m:
        return m.group(1)

    return None

def _classify_with_llm(filename: str, ocr_text: str) -> dict:
    """Fallback: ask Gemini to classify when regex is ambiguous."""
    text_head = ocr_text[:2000] if ocr_text else "(prázdný text)"
    prompt = CLASSIFICATION_LLM_PROMPT.format(filename=filename, text_head=text_head)

    try:
        response = gemini.generate(prompt)
        raw = response.text.strip()
        raw = re.sub(r'^```(?:json)?\s*', '', raw)
        raw = re.sub(r'\s*```$', '', raw)
        data = json.loads(raw)

        label = data.get("label")
        if label not in DOC_PRIORITY:
            return {"label": None, "amendment_number": None}

        return {
            "label": label,
            "amendment_number": data.get("amendment_number"),
        }
    except Exception:
        return {"label": None, "amendment_number": None}

llm_calls = 0
def classify_document(filename: str, ocr_text: str) -> dict:
    text_head = ocr_text[:3000] if ocr_text else ""
    combined = normalize_text(f"{text_head}")

    matched = []
    for doc_type, patterns in RULES.items():
        if _matches_any(combined, patterns):
            matched.append(doc_type)

    amendment_number = None
    dolozka_code = None

    if len(matched) == 1:
        label = matched[0]

        if label == "PS":
            amendment_number = _extract_amendment_number(filename, text_head)

        if label == "DOL":
            dolozka_code = _extract_dolozka_code(filename, text_head)
    elif len(matched) == 0:
        llm_result = _classify_with_llm(filename, ocr_text or "")

        global llm_calls
        llm_calls += 1

        label = llm_result["label"]
        amendment_number = llm_result.get("amendment_number")
        dolozka_code = llm_result.get("dolozka_code")
    else:
        label = _find_earliest(combined)

    priority = DOC_PRIORITY.get(label, 0) if label else 0
    if label == "PS" and amendment_number is not None:
        priority += amendment_number
    if label == "DOL" and dolozka_code is not None:
        m = re.search(r'(\d+)', dolozka_code)
        if m:
            priority += int(m.group(1))

    return {
        "label": label,
        "priority": priority,
    }


def classify_and_sort(documents: list[dict]) -> list[dict]:
    classified = []
    for doc in documents:
        classification = classify_document(
            doc.get("filename", ""),
            doc.get("ocr_text", "")
        )
        classified.append({**doc, "classification": classification})

    classified.sort(key=lambda d: d["classification"]["priority"])
    return classified


if __name__ == "__main__":
    print("CLASSIFICATION TEST")
    print("=" * 75)

    with open("input_custom.json", encoding="utf-8") as f:
        data = json.load(f)

    for item in data:
        r = classify_document(item.get("filename"), item.get("ocr_text"))
        item["label"] = r.get("label")
        print(item.get("filename"), r)

    print(f"LLM calls: {llm_calls}")

    with open("input_custom.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)