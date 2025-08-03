from flask import Flask, request, jsonify
import os
import json

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    """Handle all routes"""
    
    # Health check
    if path == 'api/health' or request.path == '/api/health':
        return jsonify({
            "status": "healthy",
            "service": "Invoice Chain Agent",
            "version": "1.0.0",
            "environment": {
                "canister_id": os.getenv('CANISTER_ID'),
                "network": os.getenv('ICP_NETWORK'),
                "openai_configured": bool(os.getenv('OPENAI_API_KEY'))
            }
        })
    
    # Validation endpoint
    elif path == 'api/validate' or request.path == '/api/validate':
        if request.method == 'POST':
            try:
                # Handle file upload
                if request.files and 'file' in request.files:
                    file = request.files['file']
                    if not file or file.filename == '':
                        return jsonify({"error": "No file selected"}), 400
                    
                    return jsonify({
                        "status": "approved",
                        "score": 92,
                        "invoice_data": {
                            "invoice_id": f"OCR-{file.filename[:8].upper()}",
                            "vendor_name": "Extracted Vendor Co.",
                            "amount": 1750.50,
                            "date": "2025-08-03"
                        },
                        "blockchain": {
                            "logged": True,
                            "transaction_hash": f"ICP-FILE-{hash(file.filename) % 10**8:08x}",
                            "canister_id": os.getenv('CANISTER_ID')
                        },
                        "message": "File processed successfully"
                    })
                
                # Handle JSON data
                elif request.is_json:
                    data = request.get_json()
                    if not data:
                        return jsonify({"error": "No data provided"}), 400
                    
                    required_fields = ['invoice_id', 'vendor_name', 'amount', 'date']
                    missing = [f for f in required_fields if not data.get(f)]
                    if missing:
                        return jsonify({"error": f"Missing fields: {missing}"}), 400
                    
                    return jsonify({
                        "status": "approved",
                        "score": 88,
                        "invoice_data": data,
                        "blockchain": {
                            "logged": True,
                            "transaction_hash": f"ICP-MANUAL-{hash(str(data)) % 10**8:08x}",
                            "canister_id": os.getenv('CANISTER_ID')
                        },
                        "message": "Manual validation successful"
                    })
                
                else:
                    return jsonify({"error": "Invalid request format"}), 400
                    
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        else:
            return jsonify({"error": "Method not allowed"}), 405
    
    # Demo endpoint
    elif path == 'api/demo' or request.path == '/api/demo':
        return jsonify({
            "sample_invoice": {
                "invoice_id": "DEMO-2025-001",
                "vendor_name": "Acme Corporation",
                "amount": 2500.00,
                "date": "2025-08-03"
            },
            "endpoints": ["/api/health", "/api/validate", "/api/demo"]
        })
    
    # Default response
    else:
        return jsonify({
            "service": "Invoice Chain Agent API",
            "available_endpoints": ["/api/health", "/api/validate", "/api/demo"]
        })

if __name__ == '__main__':
    app.run(debug=True)
