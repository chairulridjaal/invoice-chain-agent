from flask import Flask, request, jsonify
import os
import json
import requests

app = Flask(__name__)
BACKEND_URL = os.getenv('BACKEND_URL', 'http://127.0.0.1:8001')

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint proxy"""
    resp = requests.get(f"{BACKEND_URL}/health")
    return (resp.content, resp.status_code, resp.headers.items())

@app.route('/api/validate', methods=['POST'])
def validate_invoice():  # proxy to backend
    """Validate invoice endpoint"""
    try:
        if request.files and 'file' in request.files:
            # forward file upload to backend
            resp = requests.post(f"{BACKEND_URL}/upload", files={'file': request.files['file']})
        
        # Handle JSON data
        elif request.is_json:
            resp = requests.post(f"{BACKEND_URL}/submit", json=request.get_json())
        
        else:
            return jsonify({"error": "Invalid request format"}), 400
        
        return (resp.content, resp.status_code, resp.headers.items())
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/demo', methods=['GET'])
def demo():
    """Demo endpoint"""
    return jsonify({
        "sample_invoice": {
            "invoice_id": "DEMO-2025-001",
            "vendor_name": "Acme Corporation",
            "amount": 2500.00,
            "date": "2025-08-03"
        },
        "endpoints": ["/api/health", "/api/validate", "/api/demo"]
    })

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    """Handle all other routes"""
    return jsonify({
        "service": "Invoice Chain Agent API",
        "available_endpoints": ["/api/health", "/api/validate", "/api/demo"],
        "message": "API is running"
    })

if __name__ == '__main__':
    app.run(debug=True)
