#!/usr/bin/env python
"""
MongoDB Connection Test Script
Tests the connection to MongoDB Atlas cluster
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

async def test_mongodb_connection():
    """Test MongoDB connection"""
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    print(f"Connecting to MongoDB...")
    print(f"URL: {MONGODB_URL[:50]}..." if len(MONGODB_URL) > 50 else f"URL: {MONGODB_URL}")
    
    try:
        client = AsyncIOMotorClient(MONGODB_URL)
        db = client["ai_legal_assistant"]
        
        # Test connection by pinging
        await client.admin.command('ping')
        print("✓ MongoDB connection successful!")
        
        # List collections
        collections = await db.list_collection_names()
        print(f"✓ Database: ai_legal_assistant")
        print(f"✓ Collections: {collections if collections else 'No collections yet'}")
        
        # Test insert sample data
        result = await db.legal_knowledge.update_one(
            {"title": "Fourth Amendment"},
            {"$set": {
                "category": "constitutional_rights",
                "title": "Fourth Amendment",
                "description": "Protection against unreasonable searches and seizures"
            }},
            upsert=True
        )
        print(f"✓ Sample data insert/update: Success")
        
        # Test read
        doc = await db.legal_knowledge.find_one({"title": "Fourth Amendment"})
        if doc:
            print(f"✓ Sample data retrieved: {doc['title']}")
        
        client.close()
        print("\n✓ All tests passed!")
        
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check your internet connection")
        print("2. Verify MongoDB username and password")
        print("3. Check .env file for correct MONGODB_URL")
        print("4. Ensure your IP is whitelisted in MongoDB Atlas")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_mongodb_connection())
    exit(0 if success else 1)
