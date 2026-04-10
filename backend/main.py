from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List
import os
from datetime import datetime
from io import BytesIO

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    import easyocr
except ImportError:
    easyocr = None

try:
    import pytesseract
except ImportError:
    pytesseract = None

import numpy as np

try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[OK] .env file loaded")
except ImportError:
    print("[WARNING] python-dotenv not installed")
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
print(f"[OK] MongoDB URL loaded: {MONGODB_URL[:50]}...")
client = AsyncIOMotorClient(MONGODB_URL)
db = client["ai_legal_assistant"]  # Use the database from connection string


class ProblemRequest(BaseModel):
    problem: str
    language: str = "en-US"

class ProblemResponse(BaseModel):
    issue_type: str
    related_article_or_law: str
    simplified_explanation: str
    recommended_actions: List[str]

# AI-powered analysis function using NLP Engine
def analyze_problem(problem: str, language: str = "en-US") -> ProblemResponse:
    """Analyze legal problem using NLP engine"""
    try:
        result = analyze_legal_problem(problem, language=language)
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
        result = analyze_problem(request.problem, request.language)

        # Try to store in database, but don't fail if database is unavailable
        try:
            if db is not None:
                await db.problems.insert_one({
                    "problem": request.problem,
                    "language": request.language,
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

# OCR configuration
OCR_ENGINE = None
OCR_BACKEND = None
LEGAL_TERM_DICTIONARY = {
    "petitioner": "Person who files the case.",
    "affidavit": "A written statement made under oath.",
    "injunction": "A court order that requires or prevents an action.",
    "jurisdiction": "The authority of a court to hear and decide a case.",
    "plaintiff": "The person who brings a lawsuit.",
    "defendant": "The person against whom a lawsuit is filed.",
    "summons": "A legal document ordering someone to appear in court.",
    "arbitration": "A private process for resolving disputes outside court.",
    "notarize": "To have a document certified by a notary public.",
    "subpoena": "A court order requiring someone to testify or produce evidence.",
    "litigation": "The process of taking legal action in court.",
    "appeal": "A request for a higher court to review a decision.",
    "settlement": "An agreement to resolve a dispute without going to trial.",
    "deposition": "Sworn testimony taken outside of court before trial.",
    "statute": "A law passed by a legislative body.",
    "contract": "A legally binding agreement between parties."
}

if Image is None:
    print("[WARNING] PIL is not installed. OCR will be unavailable.")

# Try pytesseract first as it's more memory efficient
if pytesseract is not None and Image is not None:
    OCR_BACKEND = 'pytesseract'
    print('[OK] pytesseract OCR backend available')
elif easyocr is not None and Image is not None:
    try:
        # Use a lighter configuration for EasyOCR
        OCR_ENGINE = easyocr.Reader(['en'], gpu=False, model_storage_directory='.', download_enabled=False)
        OCR_BACKEND = 'easyocr'
        print('[OK] EasyOCR engine initialized')
    except Exception as ocr_error:
        print(f'[WARNING] EasyOCR initialization failed: {ocr_error}')
        # Fallback to pytesseract if available
        if pytesseract is not None:
            OCR_BACKEND = 'pytesseract'
            print('[OK] Falling back to pytesseract OCR backend')


async def extract_text_from_image(image_bytes: bytes) -> str:
    if Image is None:
        raise RuntimeError('PIL is required for OCR but is not installed.')

    try:
        # Try to open the image with PIL
        image = Image.open(BytesIO(image_bytes))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')

        if OCR_BACKEND == 'pytesseract':
            try:
                return pytesseract.image_to_string(image, lang='eng').strip()
            except Exception as e:
                print(f"Tesseract OCR failed: {e}")
                return "OCR processing failed. The image may not contain readable text."

        if OCR_BACKEND == 'easyocr' and OCR_ENGINE is not None:
            try:
                image_array = np.array(image)
                text_lines = OCR_ENGINE.readtext(image_array, detail=0, paragraph=True)
                return '\n'.join(text_lines).strip()
            except Exception as e:
                print(f"EasyOCR failed: {e}")
                return "OCR processing failed. The image may not contain readable text."

        # Fallback: Return a mock analysis for demo purposes
        return "Document analysis completed. This appears to be a legal document. Key terms detected: notice, legal, document. For full text extraction, please ensure the image is clear and contains readable text."
        
    except Exception as e:
        print(f"Image processing error: {e}")
        return "Unable to process image. Please ensure the file is a valid image format and contains readable text."


def detect_legal_terms(text: str) -> List[dict]:
    found_terms = []
    lower_text = text.lower()
    for term, explanation in LEGAL_TERM_DICTIONARY.items():
        if term in lower_text:
            found_terms.append({
                'term': term.capitalize(),
                'explanation': explanation
            })
    return found_terms


@app.post('/scan-document')
async def scan_document(document_image: UploadFile = File(...)):
    if OCR_BACKEND is None:
        raise HTTPException(status_code=500, detail='OCR engine is not available. Install easyocr and pillow.')

    try:
        file_bytes = await document_image.read()
        extracted_text = await extract_text_from_image(file_bytes)
        legal_terms = detect_legal_terms(extracted_text)

        return {
            'extracted_text': extracted_text,
            'legal_terms': legal_terms,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'OCR scan failed: {str(e)}')


class VoiceRequest(BaseModel):
    message: str
    language: str = "en-US"


class VoiceResponse(BaseModel):
    reply: str


@app.post('/voice-ai', response_model=VoiceResponse)
async def voice_ai_endpoint(request: VoiceRequest):
    """
    Voice AI endpoint for processing voice queries and returning responses
    """
    try:
        message = request.message.lower().strip()
        language = request.language
        
        # Simple keyword-based legal responses (optimized for low RAM)
        responses = get_legal_response(message, language)
        
        return VoiceResponse(reply=responses)
        
    except Exception as e:
        print(f"Voice AI error: {e}")
        return VoiceResponse(reply="I apologize, but I'm having trouble processing your request right now. Please try again.")


def get_legal_response(message: str, language: str) -> str:
    """
    Generate legal responses based on keyword matching (low RAM optimization)
    """
    
    # Bhojpuri responses
    if language == 'bho-IN':
        if any(keyword in message for keyword in ['police', 'pulis', 'polis', 'arrest', 'girftari', 'pakad']):
            return " police ke pakad ke liye warrant chahiye. jab tak warrant na ho, aap pakad se inkar kar sakel. aapke rights ke baare me jaankari rakhna zaruri ba."
        
        elif any(keyword in message for keyword in ['phone', 'mobile', 'call', 'phone', 'call record', 'phonwala']):
            return " police aapke phone ke tabhi le sakela jab uske paas proper warrant ba ya emergency situation ho. aap phone wapas maang sakel."
        
        elif any(keyword in message for keyword in ['fir', 'complaint', 'shikayat', 'report', 'dard']):
            return " FIR likhwaana aapka fundamental right ba. police ke FIR likhna padela. agar police inkar kare toh aap senior officer se shikayat kar sakel."
        
        elif any(keyword in message for keyword in ['bail', 'jamanat', 'bail', 'chhutti']):
            return " bail ke liye aap court mein application kar sakel. non-bailable offenses mein bail paana mushkil ho sakela. lawyer se salah lena zaroori ba."
        
        elif any(keyword in message for keyword in ['rights', 'adhikar', 'right', 'haq']):
            return " aapke constitutional rights ba: right to equality, right to freedom, right against exploitation, right to religion, cultural and educational rights, aur right to constitutional remedies."
        
        else:
            return " hum aapke legal help karne ke liye baani. kripya aapni problem detail mein bataiye jaise police arrest, phone seizure, ya FIR ke baare mein."
    
    # Hindi responses
    elif language == 'hi-IN':
        if any(keyword in message for keyword in ['police', 'pulis', 'polis', ' arrest', 'girftari']):
            return " police arrest ke liye warrant chahiye. agar aapke paas warrant nahi hai toh aap arrest se inkar kar sakte hain. aapko apne rights ke bare mein jaankari honi chahiye."
        
        elif any(keyword in message for keyword in ['phone', 'mobile', 'call', 'phone', 'call record']):
            return " police aapke phone ko legally tabhi le sakta hai jab uske paas proper warrant hai ya emergency situation ho. aap phone wapas maang sakte hain."
        
        elif any(keyword in message for keyword in ['fir', 'complaint', 'shikayat', 'report']):
            return " FIR darj karwana aap ka fundamental right hai. police ko FIR darj karna padta hai. agar police inkar kare toh aap senior officer se shikayat kar sakte hain."
        
        elif any(keyword in message for keyword in ['bail', 'jamanat', 'bail']):
            return " bail ke liye aap court mein application kar sakte hain. non-bailable offenses mein bail milna mushkil ho sakta hai. lawyer se salah lena zaroori hai."
        
        elif any(keyword in message for keyword in ['rights', 'adhikar', 'right']):
            return " aapke constitutional rights hain: right to equality, right to freedom, right against exploitation, right to religion, cultural and educational rights, aur right to constitutional remedies."
        
        else:
            return " main aapki legal help karne ke liye hun. kripya apni problem detail mein batayein jaise police arrest, phone seizure, ya FIR ke bare mein."
    
    # English responses
    else:
        if any(keyword in message for keyword in ['police', 'arrest', 'detained', 'custody']):
            return "Police generally need a warrant to arrest you except in emergency situations. You have the right to remain silent and request legal counsel. Always ask for the reason of arrest."
        
        elif any(keyword in message for keyword in ['phone', 'mobile', 'device', 'seizure', 'confiscate']):
            return "Police can only seize your phone with a proper warrant or in emergency situations. You have the right to ask for the seizure reason and request its return."
        
        elif any(keyword in message for keyword in ['fir', 'complaint', 'report', 'register']):
            return "Filing an FIR is your fundamental right. Police must register your complaint. If they refuse, you can approach senior officers or the court."
        
        elif any(keyword in message for keyword in ['bail', 'jail', 'release']):
            return "You can apply for bail in court. For non-bailable offenses, bail is at the court's discretion. Consult a lawyer for proper guidance."
        
        elif any(keyword in message for keyword in ['rights', 'constitutional', 'legal']):
            return "Your fundamental rights include: Right to Equality, Right to Freedom, Right against Exploitation, Right to Religion, Cultural and Educational Rights, and Right to Constitutional Remedies."
        
        elif any(keyword in message for keyword in ['property', 'land', 'house', 'eviction']):
            return "Property disputes require proper documentation. You cannot be evicted without due process. Always verify ownership documents and seek legal advice."
        
        elif any(keyword in message for keyword in ['consumer', 'complaint', 'product', 'service']):
            return "You can file consumer complaints for defective products or poor service. Approach consumer forums within the prescribed time limit with proper evidence."
        
        elif any(keyword in message for keyword in ['salary', 'wage', 'payment', 'employer']):
            return "Employers must pay salaries on time. You can approach labor commissioner for unpaid wages. Maintain proper employment records and communication."
        
        elif any(keyword in message for keyword in ['divorce', 'marriage', 'family', 'child']):
            return "Family matters require sensitive handling. Family courts handle divorce, child custody, and maintenance. Consider mediation before litigation."
        
        else:
            return "I'm here to help with legal guidance. Please tell me about your specific legal issue - whether it's related to police matters, property disputes, consumer rights, or any other legal concern."


# Database models for legal knowledge (example)
@app.on_event("startup")
async def startup_event():
    try:
        print("[OK] Attempting MongoDB connection...")
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
        print("[OK] MongoDB connected and initialized")
    except Exception as e:
        print(f"[WARNING] MongoDB not available: {e}")
        print("   The API will work without MongoDB for now")
