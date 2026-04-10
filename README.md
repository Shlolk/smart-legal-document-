Citizen Digital Rights Guardian
A full-stack web application that empowers citizens by analyzing legal and government-related problems in natural language and providing simplified guidance, relevant constitutional rights, and step-by-step civic actions.

🚀 Features
Natural Language Processing: AI-powered analysis of citizen complaints using advanced NLP models
Constitutional Rights Matching: Automatically identifies relevant constitutional amendments and federal laws
Simplified Legal Guidance: Provides easy-to-understand explanations in plain language
Civic Action Steps: Offers practical, step-by-step guidance for resolving issues
Responsive Web Interface: Modern, accessible UI built with React and Tailwind CSS
MongoDB Integration: Stores legal knowledge base and problem submissions
FastAPI Backend: High-performance Python API with async support
🏗️ Architecture

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐│   React Frontend│    │   FastAPI Backend│    │   MongoDB Atlas ││                 │    │                 │    │                 ││ - Problem Input │◄──►│ - NLP Analysis  │◄──►│ - Legal Knowledge││ - Results Display│    │ - API Endpoints │    │ - Problem Logs  ││ - Responsive UI  │    │ - CORS Enabled  │    │ - User Data     │└─────────────────┘    └─────────────────┘    └─────────────────┘
📋 Prerequisites
Node.js (v16 or higher) - for frontend development
Python (v3.8 or higher) - for backend API
MongoDB Atlas account (or local MongoDB) - for database
Git - for version control
🛠️ Installation & Setup
1. Clone the Repository

git clone <repository-url>cd citizen-digital-rights-guardian
2. Backend Setup

cd backend# Create virtual environmentpython -m venv venvsource venv/bin/activate  # On Windows: venv\Scripts\activate# Install dependenciespip install -r requirements.txt# Configure environment variablescp .env.example .env# Edit .env with your MongoDB Atlas connection string
Environment Variables (.env):


MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/ai_legal_assistant?retryWrites=true&w=majority
3. Frontend Setup

cd frontend# Install dependenciesnpm install# Start development servernpm run dev
4. Database Setup
The application uses MongoDB Atlas. The database will be automatically initialized with sample legal knowledge when the backend starts.

🚀 Running the Application
Development Mode
Start Backend:


cd backendsource venv/bin/activate  # On Windows: venv\Scripts\activateuvicorn main:app --reload --host 0.0.0.0 --port 8000
Start Frontend:


cd frontendnpm run dev
Access Application:

Frontend: http://localhost:5173
Backend API: http://localhost:8000
API Documentation: http://localhost:8000/docs
Production Build

# Build frontendcd frontendnpm run build# Backend can be deployed using FastAPI deployment options# (Docker, Heroku, AWS, etc.)
📚 API Documentation
Endpoints
POST /analyze-problem
Analyzes a legal problem and returns structured guidance.

Request Body:


{  "problem": "My employer hasn't paid me overtime for working 50 hours last month"}
Response:


{  "issue_type": "Wage and Hour Violation",  "related_article_or_law": "Fair Labor Standards Act (FLSA)",  "simplified_explanation": "The Fair Labor Standards Act requires employers to pay non-exempt employees one and one-half times their regular rate for hours worked over 40 in a workweek...",  "recommended_actions": [    "Gather all pay stubs and time records showing hours worked",    "Calculate total unpaid overtime wages",    "File a complaint with the U.S. Department of Labor",    "Consider consulting with an employment attorney"  ]}
GET /
Health check endpoint returning API status.

🧠 NLP Engine
The application uses a sophisticated NLP engine that:

Classifies Issues: Uses zero-shot classification and semantic search
Identifies Rights: Matches problems to constitutional amendments and laws
Generates Explanations: Creates simplified legal explanations
Suggests Actions: Provides step-by-step civic guidance
Supported Issue Categories
Police Search and Seizure (4th Amendment)
Wage Disputes (FLSA)
Harassment & Discrimination (Title VII)
Tenant Rights (Fair Housing Act)
Police Brutality (Civil Rights)
First Amendment Rights
Disability Rights (ADA)
🗄️ Database Schema
Collections
problems
Stores submitted problems and their analyses:


{  "problem": "User's complaint text",  "analysis": {    "issue_type": "Wage and Hour Violation",    "related_article_or_law": "FLSA",    "simplified_explanation": "...",    "recommended_actions": [...]  },  "timestamp": "2024-01-01T00:00:00Z"}
legal_knowledge
Legal knowledge base:


{  "category": "constitutional_rights",  "title": "Fourth Amendment",  "description": "Protection against unreasonable searches and seizures"}
🧪 Testing
Backend Tests

cd backendpython -m pytest
API Testing

# Test the API endpointcurl -X POST "http://localhost:8000/analyze-problem" \     -H "Content-Type: application/json" \     -d '{"problem": "Police searched my car without a warrant"}'
Database Connection Test

cd backendpython test_mongodb.py
📦 Dependencies
Backend (requirements.txt)
fastapi - Web framework
motor - Async MongoDB driver
transformers - NLP models (optional)
scikit-learn - Machine learning
torch - PyTorch for transformers
python-dotenv - Environment variables
pydantic - Data validation
Frontend (package.json)
vite - Build tool and dev server
tailwindcss - CSS framework (via CDN)
🔧 Configuration
Environment Variables
Variable	Description	Default
MONGODB_URL	MongoDB Atlas connection string	mongodb://localhost:27017
Optional Dependencies
The NLP engine gracefully degrades if heavy ML libraries aren't available:

Without transformers: Uses keyword matching fallback
Without torch: Uses CPU-only inference
Without scikit-learn: Basic text processing only
🚀 Deployment
Docker Deployment

# Backend DockerfileFROM python:3.9-slimWORKDIR /appCOPY requirements.txt .RUN pip install -r requirements.txtCOPY . .EXPOSE 8000CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
Cloud Platforms
Backend: Heroku, Railway, Render, AWS Lambda
Frontend: Vercel, Netlify, GitHub Pages
Database: MongoDB Atlas (already cloud-hosted)
🤝 Contributing
Fork the repository
Create a feature branch
Make your changes
Add tests if applicable
Submit a pull request
📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

⚠️ Disclaimer
This application provides general legal information and guidance based on publicly available legal knowledge. It is not a substitute for professional legal advice. Users should consult with qualified attorneys for specific legal situations.

🙏 Acknowledgments
Built with FastAPI, React, and MongoDB
NLP powered by Hugging Face Transformers
Legal knowledge base compiled from public sources
Inspired by the need for accessible legal guidance for all citizens
Made with ❤️ for digital rights and civic empowerment


