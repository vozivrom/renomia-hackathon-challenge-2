"""
Challenge 2: Vyčítání dat ze souborů (Document Data Extraction)

Input:  OCR text from insurance contract documents (main contract + amendments)
Output: Structured CRM fields extracted from the documents
"""

import os

import time

import psycopg2
from fastapi import FastAPI
import uvicorn

from db import get_db
from gemini import gemini

from extraction import extract_features
app = FastAPI(title="Challenge 2: Document Data Extraction")

@app.on_event("startup")
def init_db():
    for _ in range(15):
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute(
                """CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value JSONB,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )"""
            )
            conn.commit()
            cur.close()
            conn.close()
            return
        except Exception:
            time.sleep(1)


@app.get("/")
def health():
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    return gemini.get_metrics()


@app.post("/metrics/reset")
def reset_metrics():
    gemini.reset()
    return {"status": "reset"}

@app.post("/test-gemini")
def test_gemini():
    """Quick test to verify Gemini API key works."""
    if not gemini.enabled:
        return {"error": "GEMINI_API_KEY not set"}
    try:
        response = gemini.generate("Say 'hello' in Czech. Reply with one word only.")
        return {
            "status": "ok",
            "response": response.text,
            "metrics": gemini.get_metrics(),
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.post("/solve")
def solve(payload: dict):
    """
    Extract structured CRM fields from insurance contract documents.

    Input example:
    {
        "documents": [
            {
                "pdf_url": "https://storage.googleapis.com/.../smlouva.pdf",
                "filename": "smlouva_hlavni.pdf",
                "ocr_text": "... OCR extracted text of main contract ..."
            },
            {
                "pdf_url": "https://storage.googleapis.com/.../dodatek_1.pdf",
                "filename": "dodatek_1.pdf",
                "ocr_text": "... OCR text of amendment 1 ..."
            },
            {
                "pdf_url": "https://storage.googleapis.com/.../dodatek_2.pdf",
                "filename": "dodatek_2.pdf",
                "ocr_text": "... OCR text of amendment 2 ..."
            }
        ]
    }

    Expected output (all fields from CRM template):
    {
        "contractNumber": "POJ-2024-12345",
        "insurerName": "Generali Česká pojišťovna a.s.",
        "state": "accepted",              // enum: draft | accepted | cancelled
        "assetType": "other",              // enum: other | vehicle
        "concludedAs": "broker",           // enum: agent | broker
        "contractRegime": "individual",    // enum: individual | frame | fleet | coinsurance
        "startAt": "01.01.2024",           // DD.MM.YYYY
        "endAt": null,                     // DD.MM.YYYY or null (doba neurčitá)
        "concludedAt": "15.12.2023",       // DD.MM.YYYY
        "installmentNumberPerInsurancePeriod": 4,  // 1=yearly, 2=semi, 4=quarterly, 12=monthly
        "insurancePeriodMonths": 12,       // 12=yearly, 6=semi, 3=quarterly, 1=monthly
        "premium": {
            "currency": "czk",             // ISO 4217 lowercase
            "isCollection": false          // true if broker collects premium
        },
        "actionOnInsurancePeriodTermination": "auto-renewal",  // auto-renewal | policy-termination
        "noticePeriod": "six-weeks",       // enum or null
        "regPlate": null,                  // only for vehicle insurance
        "latestEndorsementNumber": "3",    // string, highest amendment number or null
        "note": null                       // special conditions summary or null
    }
    """
    # TODO: Implement your solution here
    #
    # Suggested approach:
    # 1. Concatenate OCR text from all documents (main contract + amendments)
    # 2. Send to Gemini with a structured extraction prompt
    # 3. Parse the response into the expected field format
    # 4. For amendments: use the latest values (amendments override base contract)
    # 5. For latestEndorsementNumber: find the highest amendment number

    documents = payload.get("documents", [])

    result = {
        "contractNumber": None,
        "insurerName": None,
        "state": "accepted",
        "assetType": "other",
        "concludedAs": "broker",
        "contractRegime": "individual",
        "startAt": None,
        "endAt": None,
        "concludedAt": None,
        "installmentNumberPerInsurancePeriod": 1,
        "insurancePeriodMonths": 12,
        "premium": {
            "currency": "czk",
            "isCollection": False,
        },
        "actionOnInsurancePeriodTermination": "auto-renewal",
        "noticePeriod": None,
        "regPlate": None,
        "latestEndorsementNumber": None,
        "note": None,
    }

    return result


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
