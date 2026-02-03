import os
import pymongo
from dotenv import load_dotenv

def init_mongo():
    load_dotenv()
    uri = os.getenv("MONGO_URI")
    
    if not uri:
        print("❌ Error: MONGO_URI not found in .env file.")
        return

    print(f"Testing connection to: {uri.split('@')[1] if '@' in uri else 'Localhost'}...")
    
    try:
        client = pymongo.MongoClient(uri, tls=True, tlsAllowInvalidCertificates=True)
        # Force a connection check
        client.admin.command('ping')
        print("✅ MongoDB Atlas Connection Successful!")
        
        db = client["risk_bot_db"]
        col_name = "contracts"
        
        # Check if collection exists
        if col_name in db.list_collection_names():
            print(f"ℹ️  Collection '{col_name}' already exists.")
        else:
            # Create explicitly (optional in Mongo, but good for confirmation)
            db.create_collection(col_name)
            print(f"✅ Collection '{col_name}' created successfully.")
            
        print("\nDatabase setup complete. Data will be stored in 'risk_bot_db.contracts'.")
        
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        print("Tip: Check if your IP address is whitelisted in MongoDB Atlas Network Access.")

if __name__ == "__main__":
    init_mongo()
