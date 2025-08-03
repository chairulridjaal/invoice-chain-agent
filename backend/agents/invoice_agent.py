from uagents import Agent, Context, Protocol, Model
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.openai_explain import explain_validation
from blockchain.integration import BlockchainIntegration
from utils.ocr_processor import process_uploaded_invoice
from utils.invoice_validator import InvoiceValidator
import json
import asyncio
from threading import Thread
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

# Define message schema
class Invoice(Model):
    invoice_id: str
    vendor_name: str
    tax_id: str
    amount: float
    date: str
    line_items: list = []
    notes: str = ""

class ValidationResult(Model):
    invoice_id: str
    status: str
    explanation: str
    score: int
    validation_details: dict

# Define agent
invoice_agent = Agent(
    name="invoice_chain_agent",
    seed="invoice_chain_agent_secret_phrase",
    port=int(os.getenv("AGENT_PORT", "8000"))
)

# Define protocol
invoice_protocol = Protocol(name="invoice_validation_protocol")

# Initialize components
blockchain = BlockchainIntegration()
validator = InvoiceValidator()

def process_invoice(invoice_data):
    """
    Multi-layered invoice validation pipeline
    
    This function implements the core enterprise invoice validation logic:
    1. Basic field validation (required fields, types, formats)
    2. ERP cross-checks (vendor approval, PO matching, credit limits)
    3. Contextual validation (business logic, timing, reasonableness)
    4. Fraud detection (suspicious patterns, risk analysis)
    5. AI-powered explanation generation
    6. Immutable logging to ICP blockchain
    """
    
    print(f"\n🔍 Processing Invoice: {invoice_data.get('invoice_id', 'Unknown')}")
    print(f"📋 Vendor: {invoice_data.get('vendor_name', 'Unknown')}")
    print(f"💰 Amount: ${float(invoice_data.get('amount', 0)):,.2f}")
    print("=" * 60)
    
    try:
        # Run comprehensive validation pipeline
        status, issues, validation_details = validator.validate_invoice(invoice_data)
        
        # Generate AI explanation
        explanation = explain_validation(invoice_data, issues, validation_details)
        
        # Log validation stages
        print(f"📊 Validation Results:")
        print(f"   Basic Validation: {'✅' if validation_details['basic_validation']['passed'] else '❌'} ({validation_details['basic_validation']['score']}/25)")
        print(f"   ERP Cross-checks: {'✅' if validation_details['erp_validation']['passed'] else '❌'} ({validation_details['erp_validation']['score']}/30)")
        print(f"   Contextual Logic: {'✅' if validation_details['contextual_validation']['passed'] else '❌'} ({validation_details['contextual_validation']['score']}/25)")
        print(f"   Fraud Detection:  {'✅' if validation_details['fraud_detection']['passed'] else '❌'} ({validation_details['fraud_detection']['score']}/20)")
        print(f"   Overall Score: {validation_details['overall_score']}/100")
        
        if issues:
            print(f"\n⚠️  Issues Found ({len(issues)}):")
            for i, issue in enumerate(issues[:5], 1):  # Show first 5 issues
                print(f"   {i}. {issue}")
            if len(issues) > 5:
                print(f"   ... and {len(issues) - 5} more issues")
        
        print(f"\n🎯 Final Decision: {status.upper()}")
        
        # Submit to blockchain if approved
        blockchain_result = None
        if status in ["approved", "approved_with_conditions"]:
            try:
                # Create comprehensive audit record with proper structure for blockchain
                audit_record = {
                    "invoice_data": invoice_data,  # Include the full invoice data
                    "status": status,
                    "explanation": explanation,
                    "validation_score": validation_details["overall_score"],
                    "timestamp": datetime.now().isoformat(),
                    "validation_stages": validation_details,
                    "issues_count": len(issues),
                    "agent_decision": "automated_approval" if status == "approved" else "conditional_approval"
                }
                
                # Submit to real ICP canister
                blockchain_result = blockchain.log_invoice(audit_record)
                print(f"🔗 Blockchain: {blockchain_result.get('message', 'Logged successfully')}")
                
            except Exception as e:
                print(f"❌ Blockchain logging failed: {e}")
                blockchain_result = {"success": False, "error": str(e)}
        else:
            print("🚫 Invoice rejected - not submitted to blockchain")
        
        # Prepare response
        result = {
            "invoice_id": invoice_data["invoice_id"],
            "status": status,
            "explanation": explanation,
            "score": validation_details["overall_score"],
            "validation_details": validation_details,
            "issues": issues,
            "processed_at": datetime.now().isoformat()
        }
        
        if blockchain_result:
            result["blockchain"] = blockchain_result
        
        print("=" * 60)
        return result
        
    except Exception as e:
        error_msg = f"Invoice processing failed: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            "invoice_id": invoice_data.get("invoice_id", "Unknown"),
            "status": "error",
            "explanation": error_msg,
            "score": 0,
            "processed_at": datetime.now().isoformat()
        }

@invoice_protocol.on_message(model=Invoice)
async def handle_invoice_message(ctx: Context, sender: str, msg: Invoice):
    """Handle incoming invoice messages via uAgent protocol"""
    ctx.logger.info(f"📨 Received invoice message: {msg.invoice_id} from {sender}")
    
    # Convert to dict for processing
    invoice_data = {
        "invoice_id": msg.invoice_id,
        "vendor_name": msg.vendor_name,
        "tax_id": msg.tax_id,
        "amount": msg.amount,
        "date": msg.date,
        "line_items": msg.line_items,
        "notes": msg.notes
    }
    
    # Process the invoice
    result = process_invoice(invoice_data)
    
    # Send response back
    response = ValidationResult(
        invoice_id=result["invoice_id"],
        status=result["status"],
        explanation=result["explanation"],
        score=result["score"],
        validation_details=result.get("validation_details", {})
    )
    
    await ctx.send(sender, response)
    ctx.logger.info(f"✅ Sent validation result for {msg.invoice_id} - Status: {result['status']}")


# Flask HTTP API for direct integration
app = Flask(__name__, static_folder='../static', static_url_path='/')

# Enable CORS for all routes
try:
    from flask_cors import CORS
    CORS(app)
except ImportError:
    print("Flask-CORS not installed, continuing without CORS support")

# Serve frontend
@app.route('/')
def serve_frontend():
    return app.send_static_file('index.html')

# Serve static assets with proper headers
@app.route('/assets/<path:filename>')
def serve_assets(filename):
    from flask import send_from_directory
    return send_from_directory(os.path.join(app.static_folder, 'assets'), filename)

# Prevent service worker issues
@app.route('/sw.js')
def service_worker():
    return '', 404

@app.route('/manifest.json')
def manifest():
    return '', 404

@app.route('/submit', methods=['POST'])
def submit_invoice():
    """HTTP endpoint for direct invoice submission"""
    try:
        invoice_data = request.get_json()
        
        # Validate required fields
        if not invoice_data:
            return jsonify({"error": "No invoice data provided"}), 400
        
        result = process_invoice(invoice_data)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"Invoice submission failed: {str(e)}"}), 400

@app.route('/invoice/<invoice_id>', methods=['GET'])
def get_invoice(invoice_id):
    """Retrieve invoice details from blockchain"""
    try:
        # In production, this would query the ICP canister
        return jsonify({
            "success": True,
            "invoice_id": invoice_id,
            "message": "Invoice retrieval from ICP blockchain (demo mode)",
            "network": "local-simulation",
            "status": "This would contain actual invoice data from the canister"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/audit/<invoice_id>', methods=['GET'])
def get_audit_logs(invoice_id):
    """Get comprehensive audit trail for an invoice"""
    try:
        # In production, this would query the ICP canister audit logs
        return jsonify({
            "success": True,
            "invoice_id": invoice_id,
            "logs": [
                {"action": "RECEIVED", "timestamp": "2025-08-03T10:00:00Z", "stage": "intake"},
                {"action": "BASIC_VALIDATION", "timestamp": "2025-08-03T10:00:01Z", "result": "passed"},
                {"action": "ERP_VALIDATION", "timestamp": "2025-08-03T10:00:02Z", "result": "passed"},
                {"action": "FRAUD_CHECK", "timestamp": "2025-08-03T10:00:03Z", "result": "passed"},
                {"action": "AI_ANALYSIS", "timestamp": "2025-08-03T10:00:04Z", "result": "approved"},
                {"action": "BLOCKCHAIN_LOGGED", "timestamp": "2025-08-03T10:00:05Z", "canister_id": "demo-canister"}
            ],
            "validation_pipeline": "4-stage enterprise validation completed",
            "message": "Complete audit trail from ICP blockchain (demo mode)"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get system-wide statistics"""
    try:
        # In production, this would aggregate data from the ICP canister
        return jsonify({
            "success": True,
            "stats": {
                "approved": 145,
                "approved_with_conditions": 23,
                "rejected": 17,
                "total_processed": 185,
                "average_score": 87.3,
                "fraud_detected": 3,
                "processing_time_avg": "1.2s"
            },
            "validation_stages": {
                "basic_validation_pass_rate": "94%",
                "erp_validation_pass_rate": "89%",
                "fraud_detection_alerts": 8,
                "ai_explanations_generated": 185
            },
            "message": "Enterprise validation statistics from ICP blockchain (demo mode)"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/health', methods=['GET'])
def health_check():
    """System health and capability check"""
    try:
        return jsonify({
            "status": "healthy",
            "agent": "invoice_chain_agent",
            "mode": "enterprise_demo",
            "capabilities": {
                "multi_layer_validation": True,
                "erp_integration": True,
                "fraud_detection": True,
                "ai_explanations": True,
                "ocr_processing": True,
                "blockchain_logging": True
            },
            "validation_pipeline": {
                "stages": 4,
                "max_score": 100,
                "components": ["basic", "erp", "contextual", "fraud"]
            },
            "icp_canister": {
                "status": "simulation",
                "message": "Ready for production deployment to Internet Computer"
            },
            "endpoints": {
                "submit": "/submit",
                "upload": "/upload",
                "get_invoice": "/invoice/<id>",
                "audit_logs": "/audit/<id>",
                "stats": "/stats"
            }
        })
    except Exception as e:
        return jsonify({"error": str(e), "status": "unhealthy"}), 500

@app.route('/upload', methods=['POST'])
def upload_invoice():
    """OCR document upload and processing"""
    try:
        print(f"📥 Received upload request")
        
        # Check if file is present
        if 'file' not in request.files:
            print("❌ No file in request")
            return jsonify({"success": False, "error": "No file uploaded"}), 400
        
        file = request.files['file']
        if file.filename == '':
            print("❌ Empty filename")
            return jsonify({"success": False, "error": "No file selected"}), 400
        
        print(f"📄 Processing file: {file.filename}")
        
        # Check file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'pdf'}
        file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        
        if file_extension not in allowed_extensions:
            print(f"❌ Unsupported file type: {file_extension}")
            return jsonify({"success": False, "error": "Unsupported file type. Please upload an image or PDF."}), 400
        
        # Process the uploaded image with OCR
        ocr_result = process_uploaded_invoice(file)
        
        print(f"🔄 OCR result: {ocr_result}")
        
        if not ocr_result['success']:
            print(f"❌ OCR failed: {ocr_result['error']}")
            return jsonify(ocr_result), 400
        
        response_data = {
            "success": True,
            "extracted_text": ocr_result['extracted_text'],
            "invoice_data": ocr_result['invoice_data'],
            "confidence": ocr_result['confidence'],
            "message": "Invoice data extracted successfully. Review and edit before submitting for validation.",
            "next_step": "Submit extracted data to /submit endpoint for full enterprise validation"
        }
        return jsonify(response_data), 200
        
    except Exception as e:
        error_msg = f"OCR processing failed: {str(e)}"
        print(f"❌ Exception in upload: {error_msg}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": error_msg}), 500

def run_flask():
    """Run Flask HTTP API server"""
    port = int(os.getenv("PORT", "8001"))
    host = os.getenv("HOST", "127.0.0.1")
    app.run(host=host, port=port, debug=False)

# Include the protocol in the agent
invoice_agent.include(invoice_protocol)

if __name__ == "__main__":
    print("🚀 Starting Enterprise Invoice Chain Agent")
    print("=" * 60)
    print("📋 Multi-Layered Validation Pipeline Active:")
    print("   1. Basic Field Validation (25 points)")
    print("   2. ERP Cross-checks (30 points)")
    print("   3. Contextual Logic (25 points)")
    print("   4. Fraud Detection (20 points)")
    print("🤖 AI-Powered Explanations: OpenAI GPT-4o-mini")
    print("🔗 Blockchain Logging: ICP Canister Integration")
    print("📄 OCR Support: Tesseract Document Processing")
    print("=" * 60)
    
    # Start Flask in a separate thread
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    port = int(os.getenv("PORT", "8001"))
    host = os.getenv("HOST", "127.0.0.1")
    agent_port = int(os.getenv("AGENT_PORT", "8000"))
    
    print(f"🌐 HTTP API Server: http://{host}:{port}")
    print(f"🔄 uAgent Protocol: http://127.0.0.1:{agent_port}")
    print(f"📊 System Dashboard: http://{host}:{port}/health")
    print(f"📤 Invoice Submission: http://{host}:{port}/submit")
    print(f"📷 OCR Document Upload: http://{host}:{port}/upload")
    print("=" * 60)
    print("🎯 Ready to process enterprise invoices with full validation pipeline!")
    print("💡 Send invoices via HTTP POST or uAgent protocol messages")
    
    # Start the agent (this will block)
    invoice_agent.run()