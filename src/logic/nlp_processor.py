import spacy
from langdetect import detect


# Load spaCy model (ensure it's installed via 'python -m spacy download en_core_web_sm')
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # Fallback if not downloaded yet
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

def extract_entities(text):
    """
    Extracts key entities like ORG, PERSON, DATE, MONEY using spaCy.
    """
    doc = nlp(text)
    entities = {
        "PARTIES": [],
        "DATES": [],
        "MONEY": [],
        "GPE": [] # Jurisdiction often falls here
    }
    
    for ent in doc.ents:
        if ent.label_ == "ORG" or ent.label_ == "PERSON":
            if ent.text not in entities["PARTIES"]:
                entities["PARTIES"].append(ent.text)
        elif ent.label_ == "DATE":
            if ent.text not in entities["DATES"]:
                entities["DATES"].append(ent.text)
        elif ent.label_ == "MONEY":
            if ent.text not in entities["MONEY"]:
                entities["MONEY"].append(ent.text)
        elif ent.label_ == "GPE":
            if ent.text not in entities["GPE"]:
                entities["GPE"].append(ent.text)
                
    return entities

def detect_language(text):
    """
    Detects the language of the text.
    Returns: 'en', 'hi', or other codes.
    """
    try:
        lang = detect(text)
        return lang
    except:
        return "unknown"

def split_into_clauses(text):

    """
    Basic heuristic to split text into potential clauses.
    Real legal doc splitting is harder, but we'll use paragraph breaks and numbering.
    """
    # Simple split by newlines for now, or regex for "1.", "2.1", etc.
    # This is a placeholder for more robust segmentation.
    paragraphs = [p.strip() for p in text.split('\n') if len(p.strip()) > 50]
    return paragraphs
