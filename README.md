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
📋 Prerequisites
Node.js (v16 or higher) - for frontend development
Python (v3.8 or higher) - for backend API
MongoDB Atlas account (or local MongoDB) - for database
Git - for version control
🛠️ Installation & Setup
1. Clone the Repository
2. Backend Setup
Environment Variables (.env):

3. Frontend Setup
4. Database Setup
The application uses MongoDB Atlas. The database will be automatically initialized with sample legal knowledge when the backend starts.

🚀 Running the Application
Development Mode
Start Backend:

Start Frontend:

Access Application:

Frontend: http://localhost:5173
Backend API: http://localhost:8000
API Documentation: http://localhost:8000/docs
Production Build
📚 API Documentation
Endpoints
POST /analyze-problem
Analyzes a legal problem and returns structured guidance.

Request Body:

Response:

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

legal_knowledge
Legal knowledge base:

🧪 Testing
Backend Tests
API Testing
Database Connection Test
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
Cloud Platforms
Backend:  Railway, Render,
Frontend: Vercel,  GitHub Pages
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