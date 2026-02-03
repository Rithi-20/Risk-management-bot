import re
from langdetect import detect

def extract_entities(text):
    """
    Heuristic-based entity extraction (No Heavy Dependencies).
    Extracts PARTIES (ORG/PERSON), DATES, MONEY, and GPE.
    """
    entities = {
        "PARTIES": [],
        "DATES": [],
        "MONEY": [],
        "GPE": [] 
    }
    
    # 1. Extract Money (e.g., $100, Rs. 500, 10,000 USD)
    money_pattern = r'(\$|Rs\.|INR|USD)\s?\d+(?:,\d+)*(?:\.\d+)?'
    entities["MONEY"] = list(set(re.findall(money_pattern, text)))

    # 2. Extract Dates (e.g., 12/05/2023, Jan 1st, 2024, 20-Oct-2022)
    date_pattern = r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4})|(?:\d{1,2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4})\b'
    entities["DATES"] = list(set(re.findall(date_pattern, text)))

    # 3. Simple Parties (Capitalized words followed by Co, Ltd, Inc, Private)
    party_pattern = r'\b[A-Z][a-z]+ (?:Co\.|Ltd\.|Inc\.|LLP|Corp\.|Private Limited|Limited)\b'
    entities["PARTIES"] = list(set(re.findall(party_pattern, text)))

    # 4. Fallback: If nothing found, look for common patterns like "between [X] and [Y]"
    if not entities["PARTIES"]:
        between_match = re.search(r'between\s+([^,and]+)(?:\s+and\s+|\s*,\s*)([^,.]+)', text, re.IGNORECASE)
        if between_match:
            entities["PARTIES"] = [between_match.group(1).strip(), between_match.group(2).strip()]

    return entities

def detect_language(text):
    """
    Detects the language of the text.
    """
    try:
        lang = detect(text[:500])
        return lang
    except:
        return "en"

def split_into_clauses(text):
    """
    Splits text into clauses based on paragraph breaks and numbering.
    """
    paragraphs = [p.strip() for p in text.split('\n') if len(p.strip()) > 50]
    return paragraphs
