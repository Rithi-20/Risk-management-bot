import os
import pymongo
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# MongoDB Config
# Note: Ensure IP Whitelist in Atlas includes 0.0.0.0/0 or your current IP
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "risk_bot_db" 
COLLECTION_NAME = "contracts"

def get_db_connection():
    try:
        # RetryWrites and SSL are often needed for Atlas
        client = pymongo.MongoClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=True) 
        db = client[DB_NAME]
        return db[COLLECTION_NAME]
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None

def save_contract_analysis(filename, text, entities, risk_analysis, overall_assessment):
    """
    Saves the contract analysis result to MongoDB.
    """
    collection = get_db_connection()
    if collection is None:
        return False

    document = {
        "filename": filename,
        "upload_date": datetime.now(),
        "entities": entities,
        "risk_overall_score": overall_assessment.get('overall_score'),
        "risk_summary": overall_assessment.get('summary'),
        "clauses_analyzed_count": len(risk_analysis),
        "full_analysis": risk_analysis, # Storing the full JSON analysis
        # "raw_text": text # Optional: might be too large, uncomment if needed
    }

    try:
        result = collection.insert_one(document)
        return str(result.inserted_id)
    except Exception as e:
        print(f"Error saving to DB: {e}")
        return False

def get_recent_contracts(limit=5):
    """
    Retrieves the last N contracts analyzed.
    """
    collection = get_db_connection()
    if collection is None:
        return []
    
    try:
        cursor = collection.find({}, {"filename": 1, "upload_date": 1, "risk_overall_score": 1}).sort("upload_date", -1).limit(limit)
        return list(cursor)
    except Exception as e:
        print(f"Error fetching history: {e}")
        return []
