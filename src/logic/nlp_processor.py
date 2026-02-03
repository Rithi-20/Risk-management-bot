import spacy
from langdetect import detect


# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # On many cloud platforms, you need to use the full name if it's not linked
    try:
        nlp = spacy.load("en_core_web_sm")
    except:
        # Final fallback for minimal functionality if spaCy fails entirely
        nlp = None

def extract_entities(text):
    """
    Extracts key entities like ORG, PERSON, DATE, MONEY using spaCy.
    """
    entities = {
        "PARTIES": [],
        "DATES": [],
        "MONEY": [],
        "GPE": [] 
    }
    
    if nlp is None:
        return entities

    doc = nlp(text)
    
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
