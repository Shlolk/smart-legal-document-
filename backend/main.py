from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List
import os
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ .env file loaded")
except ImportError:
    print("⚠️  python-dotenv not installed")
    pass

from nlp_engine import analyze_legal_problem

app = FastAPI(title="Citizen Digital Rights Guardian API")



# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow local frontend access
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
print(f"✓ MongoDB URL loaded: {MONGODB_URL[:50]}...")
client = AsyncIOMotorClient(MONGODB_URL)
db = client["ai_legal_assistant"]  # Use the database from connection string


class ProblemRequest(BaseModel):
    problem: str

class ProblemResponse(BaseModel):
    issue_type: str
    related_article_or_law: str
    simplified_explanation: str
    recommended_actions: List[str]

# AI-powered analysis function using NLP Engine
def analyze_problem(problem: str) -> ProblemResponse:
    """Analyze legal problem using NLP engine"""
    try:
        result = analyze_legal_problem(problem)
        return ProblemResponse(
            issue_type=result.get("issue_type", "Legal Issue"),
            related_article_or_law=result.get("related_article_or_law", "Consult Attorney"),
            simplified_explanation=result.get("simplified_explanation", ""),
            recommended_actions=result.get("recommended_actions", [])
        )
    except Exception as e:
        raise ValueError(f"Error analyzing problem: {str(e)}")


@app.post("/analyze-problem", response_model=ProblemResponse)
async def analyze_problem_endpoint(request: ProblemRequest):
    try:
        result = analyze_problem(request.problem)

        # Try to store in database, but don't fail if database is unavailable
        try:
            if db is not None:
                await db.problems.insert_one({
                    "problem": request.problem,
                    "analysis": result.dict(),
                    "timestamp": datetime.utcnow()
                })
        except Exception as db_error:
            print(f"Database storage failed: {db_error}")

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Citizen Digital Rights Guardian API"}

# Database models for legal knowledge (example)
@app.on_event("startup")
async def startup_event():
    try:
        print("✓ Attempting MongoDB connection...")
        # Create indexes if needed
        await db.legal_knowledge.create_index("category")
        # Insert some sample data
        sample_data = [
            {
                "category": "constitutional_rights",
                "title": "Fourth Amendment",
                "description": "Protection against unreasonable searches and seizures"
            },
            {
                "category": "labor_law",
                "title": "Fair Labor Standards Act",
                "description": "Federal law regulating minimum wage and overtime"
            }
        ]
        # Insert if not exists
        for item in sample_data:
            await db.legal_knowledge.update_one(
                {"title": item["title"]},
                {"$set": item},
                upsert=True
            )
        print("✓ MongoDB connected and initialized")
    except Exception as e:
        print(f"⚠️  MongoDB not available: {e}")
        print("   The API will work without MongoDB for now")
