DOC_PRIORITY = {
    "VPP": 100,
    "ZPP": 200,
    "DPP": 300,
    "PS": 400,
    "SUR": 500,
    "DOL": 600,
}

RULES = {
    "DOL": [
        r'dolozka\s+(?:pp|dop)\s*\d+',
        r'dolozka\s+c\.\s*\d+',
        r'dolozka\s+k\s+pojistne\s+smlouve',
        r'\bdolozka\b.*odchylne\s+od',
        r'\bdop\s*\d{2,3}\b',
    ],
    "PS": [
        r'pojistna\s+smlouva\s',
        r'pojistna\s+smlouva\s+c',
        r'pojistna\s+smlouva\s+cislo',
        r'pojistnou\s+smlouvu\s+c',
        r'kalkulacni\s+dodatek\s+c\.\s*\d+',
        r'dodatek\s+c\.',
        r'dodatek\s+c\.\s*\d+',
        r'nalezitosti\s+dodatku',
        r'nalezitosti\s+pojistne\s+smlouvy',
        r'\bd\d+[\-_]k[\-_]ps\b',
    ],
    "SUR": [
        r'smluvni\s+ujednani\s+k\s+pojistne\s+smlouve',
        r'smluvni\s+ujednani\s+(?:renomia|spolecnosti)',
        r'\bsur\b',
        r'smluvni\s+ujednani\s',
    ],
    "DPP": [
        r'doplnkove\s+pojistne\s+podminky',
        r'doplnkove\s+podminky\s+(?:pro|k)\s+pojisteni',
        r'\bdpp\b',
    ],
    "ZPP": [
        r'zvlastni\s+pojistne\s+podminky',
        r'\bzpp[\-\s]?(?:op|mp|st)',
        r'\bzpp\b',
    ],
    "VPP": [
        r'vseobecne\s+pojistne\s+podminky',
        r'pojistne\s+podminky\s+odpovednosti\s+za\s+ujmu',
        r'\bvpp[\-\s]?p\s*\d',
        r'\bvpp\b',
    ],
}

CLASSIFICATION_LLM_PROMPT = """Klasifikuj tento český pojišťovací dokument do jedné z kategorií podle obshahu:

VPP - Všeobecné pojistné podmínky
ZPP - Zvláštní pojistné podmínky
DPP - Doplňkové pojistné podmínky
SUR - Smluvní ujednání
PS - Pojistná smlouva nebo její dodatek
DOL - Doložka ke smlouvě

Soubor: {filename}
Text: {text_head}

Odpověz POUZE JSON: {{"label": "XXX", "amendment_number": N, "dolozka_code": "YYY"}}
label = jedno z: VPP, ZPP, DPP, SUR, PS, DOL, pokud nic nevyhovuje, vrat null
amendment_number = číslo dodatku (1, 2, 3...) pokud je dokument dodatek k PS, jinak null
dolozka_code = kód doložky (např. "PP 001", "DOP 003") pokud je dokument doložka, jinak null
"""