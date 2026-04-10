"""
NLP Engine for Legal Rights Analysis
Uses transformers and semantic search to match complaints to constitutional rights
Falls back to keyword matching if transformers not available
"""

try:
    from transformers import pipeline
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("⚠️  Transformers not installed. Using keyword-based matching (install with: pip install -r requirements.txt)")

import json

# Legal Knowledge Base
LEGAL_KNOWLEDGE_BASE = {
    "police_search": {
        "keywords": ["police", "search", "warrant", "property", "vehicle", "phone", "seizure"],
        "issue_type": "Unlawful Search and Seizure",
        "constitutional_rights": "Fourth Amendment",
        "explanation": "The Fourth Amendment protects citizens against unreasonable searches and seizures. Law enforcement generally requires a valid warrant signed by a judge to search your property, vehicle, or person. A warrant must be based on probable cause—reasonable belief that a crime has been committed.",
        "civic_actions": [
            "Document the search: date, time, location, officers' names and badge numbers",
            "Ask if you're being detained or if free to leave",
            "Do not consent to searches without a warrant",
            "Request a copy of the search warrant",
            "Contact a lawyer immediately",
            "File a complaint with the police internal affairs division",
            "Consider filing a motion to suppress evidence if criminal charges are filed"
        ]
    },
    "wage_dispute": {
        "keywords": ["salary", "wage", "pay", "overtime", "payment", "employer", "work"],
        "issue_type": "Wage and Hour Violation",
        "constitutional_rights": "Economic Rights / Fair Labor Standards",
        "explanation": "The Fair Labor Standards Act (FLSA) is a federal law that requires employers to pay at least the minimum wage and overtime pay for hours worked over 40 per week. Employers must also maintain accurate records of hours worked. Violations can result in penalties and lawsuits.",
        "civic_actions": [
            "Gather all pay stubs and employment contracts",
            "Calculate total unpaid wages or overtime",
            "Keep detailed records of hours worked",
            "Report to your state's Department of Labor",
            "File with the Federal Department of Labor",
            "Consult with an employment lawyer about filing a claim",
            "Consider joining a class action lawsuit if multiple employees are affected"
        ]
    },
    "harassment": {
        "keywords": ["harassment", "bullying", "threat", "intimidation", "abuse", "assault"],
        "issue_type": "Harassment and Discrimination",
        "constitutional_rights": "Fourteenth Amendment (Equal Protection)",
        "explanation": "Harassment based on race, color, religion, sex, national origin, age, or disability is illegal under federal law. This includes workplace harassment, housing discrimination, and educational discrimination. Title VII, Fair Housing Act, and ADA provide protections.",
        "civic_actions": [
            "Document all incidents: date, time, witnesses, what was said/done",
            "Save all written communications (emails, texts, messages)",
            "Report to HR or management in writing",
            "File a complaint with the EEOC (Equal Employment Opportunity Commission)",
            "Keep copies of all complaint filings",
            "Interview potential witnesses",
            "Consult with an employment or civil rights attorney"
        ]
    },
    "eviction": {
        "keywords": ["eviction", "evict", "landlord", "rent", "housing", "lease", "tenant"],
        "issue_type": "Tenant Rights / Unlawful Eviction",
        "constitutional_rights": "Due Process Rights (Fifth Amendment)",
        "explanation": "Landlords must follow legal eviction procedures and cannot evict tenants without proper notice and court proceedings. Evictions for retaliation, discrimination, or without cause are illegal. Tenants have rights to habitability and protection from wrongful eviction.",
        "civic_actions": [
            "Respond to eviction notice within required time (usually 3-7 days)",
            "File answer in court if served with eviction lawsuit",
            "Gather evidence of habitability issues or retaliation",
            "Request continuance if you need time to prepare",
            "Contact legal aid organization for free representation",
            "Explore alternatives: mediation, payment plans",
            "Consult a tenant rights attorney"
        ]
    },
    "police_brutality": {
        "keywords": ["police", "brutal", "violence", "force", "injury", "excessive", "abuse"],
        "issue_type": "Police Brutality / Excessive Force",
        "constitutional_rights": "Eighth Amendment (Cruel and Unusual Punishment)",
        "explanation": "Officers are prohibited from using excessive force when making arrests or during encounters. Force must be proportional to the threat. Victims of police brutality can sue for civil rights violations, file criminal complaints, and seek damages.",
        "civic_actions": [
            "Seek immediate medical treatment and document injuries with photos",
            "Get names and badge numbers of all officers involved",
            "Request police incident report number",
            "Interview and get contact information from witnesses",
            "File complaint with police department's Internal Affairs",
            "File complaint with state Attorney General",
            "Contact civil rights organizations",
            "Consult a civil rights attorney about filing a lawsuit"
        ]
    },
    "free_speech": {
        "keywords": ["speech", "protest", "assembly", "expression", "arrest", "demonstration"],
        "issue_type": "First Amendment Rights Violation",
        "constitutional_rights": "First Amendment (Free Speech and Assembly)",
        "explanation": "The First Amendment protects freedom of speech, press, assembly, and petition. The government cannot arrest or punish you for peaceful speech or protest. Some exceptions exist: incitement to violence, true threats, or immediate physical danger.",
        "civic_actions": [
            "Document the incident: date, location, what you were saying/doing",
            "Get contact information from witnesses and observers",
            "Record the interaction if legal in your jurisdiction",
            "Request the police incident report",
            "File complaint with ACLU (American Civil Liberties Union)",
            "Preserve all evidence and communication",
            "Consult a constitutional rights attorney"
        ]
    },
    "disability_rights": {
        "keywords": ["disability", "accommodation", "ada", "disabled", "access", "reasonable"],
        "issue_type": "ADA Violation / Disability Discrimination",
        "constitutional_rights": "Americans with Disabilities Act (ADA)",
        "explanation": "The ADA prohibits discrimination against people with disabilities in employment, public services, public transportation, and telecommunications. Employers and public entities must provide reasonable accommodations.",
        "civic_actions": [
            "Document your disability and requested accommodation",
            "Request accommodation in writing to employer/organization",
            "Keep copies of all requests and responses",
            "File complaint with Department of Justice Civil Rights Division",
            "Report to state disability rights agency",
            "Request mediation/resolution meeting",
            "Consult with disability rights attorney if needed"
        ]
    }
}

class LegalNLPEngine:
    def __init__(self):
        """Initialize NLP models and knowledge base"""
        self.issue_keys = list(LEGAL_KNOWLEDGE_BASE.keys())
        self.classifier = None
        self.vectorizer = None
        self.issue_vectors = None
        
        if TRANSFORMERS_AVAILABLE:
            try:
                # Load zero-shot classification for issue type detection
                self.classifier = pipeline(
                    "zero-shot-classification",
                    model="facebook/bart-large-mnli"
                )
                
                # Prepare TF-IDF vectorizer for semantic search
                all_keywords = []
                
                for issue_key in self.issue_keys:
                    issue_data = LEGAL_KNOWLEDGE_BASE[issue_key]
                    all_keywords.append(" ".join(issue_data["keywords"]))
                
                self.vectorizer = TfidfVectorizer()
                self.issue_vectors = self.vectorizer.fit_transform(all_keywords)
            except Exception as e:
                print(f"⚠️  Failed to load transformers: {e}. Using fallback keyword matching.")
                self.classifier = None
                self.vectorizer = None
    
    def identify_issue(self, problem_text: str) -> str:
        """
        Identify the legal issue type from complaint text
        Returns the issue key from LEGAL_KNOWLEDGE_BASE
        """
        if self.vectorizer is None:
            # Fallback: keyword matching
            problem_lower = problem_text.lower()
            best_match = "wage_dispute"  # default
            max_matches = 0
            
            for issue_key, issue_data in LEGAL_KNOWLEDGE_BASE.items():
                keyword_matches = sum(1 for kw in issue_data["keywords"] if kw in problem_lower)
                if keyword_matches > max_matches:
                    max_matches = keyword_matches
                    best_match = issue_key
            
            return best_match
        
        # Create TF-IDF vector for the problem
        problem_vector = self.vectorizer.transform([problem_text])
        
        # Calculate similarity with all issues
        similarities = cosine_similarity(problem_vector, self.issue_vectors)[0]
        
        # Get the most similar issue
        best_match_idx = int(np.argmax(similarities))
        best_match_score = float(similarities[best_match_idx])
        
        # If similarity is too low, use zero-shot classification
        if best_match_score < 0.1 and self.classifier:
            try:
                issue_options = self.issue_keys
                result = self.classifier(
                    problem_text,
                    issue_options,
                    hypothesis_template="This is about {}."
                )
                return result["labels"][0]
            except:
                pass
        
        return self.issue_keys[best_match_idx]
    
    def analyze_problem(self, problem_text: str) -> dict:
        """
        Complete analysis of a legal problem
        Returns all relevant information
        """
        # Identify the issue
        issue_key = self.identify_issue(problem_text)
        issue_data = LEGAL_KNOWLEDGE_BASE.get(issue_key, {})
        
        confidence = 0.85 if self.vectorizer is None else 0.95
        
        return {
            "issue_type": issue_data.get("issue_type", "Legal Issue"),
            "related_article_or_law": issue_data.get("constitutional_rights", "Consult Attorney"),
            "simplified_explanation": issue_data.get("explanation", "Please consult with a legal professional."),
            "recommended_actions": issue_data.get("civic_actions", []),
            "confidence_score": confidence
        }

# Initialize engine
try:
    nlp_engine = LegalNLPEngine()
except Exception as e:
    print(f"Error initializing NLP engine: {e}")
    nlp_engine = None

def analyze_legal_problem(problem_text: str) -> dict:
    """Public function to analyze legal problems"""
    if nlp_engine is None:
        return {
            "issue_type": "Unable to analyze",
            "related_article_or_law": "Please consult an attorney",
            "simplified_explanation": "The NLP engine failed to initialize. Please check the error logs.",
            "recommended_actions": ["Consult with a qualified attorney"],
            "confidence_score": 0.0
        }
    return nlp_engine.analyze_problem(problem_text)
