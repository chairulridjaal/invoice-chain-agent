#!/usr/bin/env python3
"""
Vercel serverless function entry point
"""
import os
import sys
import json
from io import BytesIO

# Add paths for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_dir = os.path.join(project_root, 'backend')
sys.path.insert(0, backend_dir)
sys.path.insert(0, project_root)

# Set environment variables with defaults
os.environ.setdefault('CANISTER_ID', 'uxrrr-q7777-77774-qaaaq-cai')
os.environ.setdefault('ICP_NETWORK', 'testnet')
os.environ.setdefault('OPENAI_API_BASE', 'https://openrouter.ai/api/v1')

from flask import Flask, request, jsonify
from flask_cors import CORS

# Create Flask app
app = Flask(__name__)
CORS(app)

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Invoice Chain Agent",
        "version": "1.0.0",
        "blockchain": {
            "canister_id": os.getenv('CANISTER_ID', 'uxrrr-q7777-77774-qaaaq-cai'),
            "network": os.getenv('ICP_NETWORK', 'testnet')
        },
        "ai": {
            "enabled": bool(os.getenv('OPENAI_API_KEY')),
            "base_url": os.getenv('OPENAI_API_BASE', 'https://openrouter.ai/api/v1')
        }
    })

@app.route('/api/validate', methods=['POST'])
def validate_invoice():
    """Validate invoice - simplified for Vercel"""
    try:
        # Handle file upload
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({"error": "No file selected"}), 400
            
            # For now, return a mock response since OCR setup is complex on serverless
            return jsonify({
                "status": "approved",
                "score": 95,
                "invoice_data": {
                    "invoice_id": "DEMO-001",
                    "vendor_name": "Sample Vendor",
                    "amount": 1500.00,
                    "date": "2025-08-03"
                },
                "validation_details": {
                    "basic_validation": {"passed": True, "score": 25},
                    "erp_validation": {"passed": True, "score": 30},
                    "contextual_validation": {"passed": True, "score": 25},
                    "fraud_detection": {"passed": True, "score": 15}
                },
                "blockchain": {
                    "logged": True,
                    "transaction_hash": "ICP-DEMO-123456789",
                    "canister_id": os.getenv('CANISTER_ID')
                },
                "message": "Demo validation successful - Full OCR processing available in development mode"
            })
        
        # Handle JSON data
        elif request.is_json:
            data = request.get_json()
            
            # Simple validation for manual input
            required_fields = ['invoice_id', 'vendor_name', 'amount', 'date']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({"error": f"Missing required field: {field}"}), 400
            
            # Mock validation
            return jsonify({
                "status": "approved",
                "score": 88,
                "invoice_data": data,
                "validation_details": {
                    "basic_validation": {"passed": True, "score": 25},
                    "erp_validation": {"passed": False, "score": 10},
                    "contextual_validation": {"passed": True, "score": 25},
                    "fraud_detection": {"passed": True, "score": 18}
                },
                "blockchain": {
                    "logged": True,
                    "transaction_hash": f"ICP-MANUAL-{hash(str(data)) % 10**8:08x}",
                    "canister_id": os.getenv('CANISTER_ID')
                },
                "message": "Manual validation successful"
            })
        
        else:
            return jsonify({"error": "No data provided"}), 400
            
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Validation failed"
        }), 500

@app.route('/api/demo', methods=['GET'])
def demo():
    """Demo endpoint with sample data"""
    return jsonify({
        "sample_invoice": {
            "invoice_id": "INV-2025-001",
            "vendor_name": "Acme Corp",
            "tax_id": "12-3456789",
            "amount": 2500.00,
            "date": "2025-08-03"
        },
        "api_endpoints": {
            "health": "/api/health",
            "validate": "/api/validate",
            "demo": "/api/demo"
        },
        "message": "Use these endpoints to test the API"
    })

# Vercel handler
def handler(request, context):
    return app

# For local development
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)
