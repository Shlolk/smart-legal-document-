from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# SERP API configuration
SERPER_API_KEY = os.getenv('SERPER_API_KEY', '')  # You'll need to set this in your .env file
SERPER_API_URL = 'https://google.serper.dev/search'

@app.route('/search', methods=['POST'])
def search_legal_query():
    """
    Search endpoint that queries SERP API for legal/government information
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data['query']
        
        if not SERPER_API_KEY:
            return jsonify({'error': 'SERP API key not configured'}), 500
        
        # Add legal/government context to the search query
        enhanced_query = f"{query} legal government site:.gov OR site:.org"
        
        # Make request to SERP API
        headers = {
            'X-API-KEY': SERPER_API_KEY,
            'Content-Type': 'application/json'
        }
        
        payload = {
            'q': enhanced_query,
            'num': 10  # Number of results to return
        }
        
        response = requests.post(SERPER_API_URL, headers=headers, json=payload)
        
        if response.status_code != 200:
            print(f"SERP API Error: {response.status_code} - {response.text}")
            return jsonify({'error': f'Search service unavailable: {response.status_code}'}), 500
        
        search_results = response.json()
        
        # Extract relevant information from SERP API response
        results = []
        if 'organic' in search_results:
            for item in search_results['organic'][:8]:  # Limit to 8 results
                result = {
                    'title': item.get('title', ''),
                    'snippet': item.get('snippet', ''),
                    'link': item.get('link', ''),
                    'displayLink': item.get('displayLink', '')
                }
                results.append(result)
        
        return jsonify({
            'success': True,
            'query': query,
            'results': results,
            'total_results': len(results)
        })
        
    except Exception as e:
        return jsonify({'error': f'Search failed: {str(e)}'}), 500

@app.route('/', methods=['GET'])
def home():
    """Home endpoint"""
    return jsonify({
        'message': 'Legal Search API Server',
        'version': '1.0.0',
        'endpoints': {
            'search': 'POST /search - Search legal information',
            'health': 'GET /health - Health check'
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Legal Search API',
        'version': '1.0.0'
    })

if __name__ == '__main__':
    print("Starting Legal Search Server...")
    print("Make sure to set SERPER_API_KEY in your .env file")
    app.run(debug=True, host='0.0.0.0', port=5001)
