# MongoDB Connection Setup
# This file demonstrates how to connect to MongoDB

from pymongo import MongoClient
import os

def get_database():
    # Replace with your MongoDB connection string
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    
    client = MongoClient(MONGODB_URL)
    
    # Database name
    db_name = "ai_legal_assistant"
    
    return client[db_name]

# Example usage
if __name__ == "__main__":
    db = get_database()
    
    # Test connection
    try:
        db.command('ping')
        print("Connected to MongoDB successfully!")
        
        # Example: Insert sample legal knowledge
        legal_collection = db["legal_knowledge"]
        
        sample_documents = [
            {
                "category": "constitutional_rights",
                "title": "Fourth Amendment",
                "description": "Protection against unreasonable searches and seizures",
                "articles": ["No unreasonable searches and seizures"]
            },
            {
                "category": "labor_law",
                "title": "Fair Labor Standards Act",
                "description": "Federal law regulating minimum wage and overtime",
                "procedures": ["File wage claim with state labor department"]
            }
        ]
        
        # Insert if not exists
        for doc in sample_documents:
            legal_collection.update_one(
                {"title": doc["title"]},
                {"$set": doc},
                upsert=True
            )
        
        print("Sample data inserted successfully!")
        
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        print("Make sure MongoDB is running on localhost:27017 or update MONGODB_URL")