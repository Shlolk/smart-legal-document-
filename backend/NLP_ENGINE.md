# NLP Legal Rights Analysis Engine

## Overview
The NLP engine uses advanced natural language processing and machine learning to analyze citizen complaints and provide legal guidance.

## Components

### 1. **Issue Classification**
- Uses zero-shot classification (Facebook BART) to identify legal issue types
- Semantic search with TF-IDF vectorization to match complaints to known issues
- Hybrid approach: keyword matching + neural classification for accuracy

### 2. **Constitutional Rights Identification**
Matches issues to relevant:
- Constitutional amendments (1st, 4th, 5th, 8th, 14th Amendment rights)
- Federal laws (FLSA, ADA, Fair Housing Act, Title VII)
- State labor codes and tenant rights

### 3. **Legal Explanation Generation**
- Simplified, non-legal language explanations
- Context-specific to the identified issue
- References to applicable laws and rights

### 4. **Civic Action Suggestions**
Step-by-step procedural guidance:
- Documentation steps
- Agency reporting procedures
- Legal consultation pathways
- Advocacy organization contacts

## Supported Issue Categories

1. **Police Search and Seizure** - Fourth Amendment violations
2. **Wage Disputes** - FLSA violations, unpaid wages, overtime
3. **Harassment and Discrimination** - Title VII, Equal Protection
4. **Tenant Rights** - Unlawful eviction, habitability
5. **Police Brutality** - Excessive force, civil rights violations
6. **First Amendment Rights** - Free speech, assembly, protest
7. **Disability Rights** - ADA violations, reasonable accommodation

## How It Works

```
User Input (Natural Language) 
    ↓
NLP Engine Issue Classification
    ↓
Semantic Matching to Legal Knowledge Base
    ↓
Constitutional Rights Identification
    ↓
Generate Simplified Explanation
    ↓
Suggest Civic Actions
    ↓
Return Structured Response
```

## Installation

```bash
cd backend
pip install -r requirements.txt
```

First run will download the transformer models (~2GB).

## Usage

```python
from nlp_engine import analyze_legal_problem

result = analyze_legal_problem("Police took my phone without a warrant")

print(result["issue_type"])                    # "Unlawful Search and Seizure"
print(result["related_article_or_law"])        # "Fourth Amendment"
print(result["simplified_explanation"])        # Legal explanation
print(result["recommended_actions"])           # List of civic actions
```

## API Example

```bash
POST http://localhost:8000/analyze-problem
Content-Type: application/json

{
  "problem": "My employer hasn't paid me overtime for working 50 hours last month"
}
```

Response:
```json
{
  "issue_type": "Wage and Hour Violation",
  "related_article_or_law": "Fair Labor Standards Act (FLSA)",
  "simplified_explanation": "The Fair Labor Standards Act requires ...",
  "recommended_actions": [
    "Gather all pay stubs and employment contracts",
    "Calculate total unpaid wages...",
    ...
  ]
}
```

## Models Used

- **Zero-shot Classification**: facebook/bart-large-mnli
  - Classifies legal issues without fine-tuning
  - Can recognize new issue types not in training data

- **TF-IDF Vectorization**: scikit-learn
  - Semantic similarity matching
  - Efficient keyword-based retrieval

## Extensibility

Add new issue types to `LEGAL_KNOWLEDGE_BASE` in `nlp_engine.py`:

```python
"new_issue": {
    "keywords": ["keyword1", "keyword2"],
    "issue_type": "Issue Name",
    "constitutional_rights": "Relevant Amendment/Law",
    "explanation": "Simplified explanation...",
    "civic_actions": [
        "Action 1",
        "Action 2",
        ...
    ]
}
```

## Performance Notes

- First run loads transformer models (~2-3 minutes)
- Subsequent requests: <1 second response time
- Runs completely locally (no external API calls)
- No authentication required
- Works offline after initial setup
