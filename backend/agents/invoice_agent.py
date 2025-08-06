from uagents import Agent, Context, Protocol, Model
import os
import sys
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')
load_dotenv(env_path)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Add root directory to path for blockchain integration
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
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
        
        # Submit to blockchain - log all invoices for audit trail
        blockchain_result = None
        try:
            # Create comprehensive audit record with proper structure for blockchain
            # Ensure invoice_data has 'id' field for blockchain integration
            if 'id' not in invoice_data and 'invoice_id' in invoice_data:
                invoice_data['id'] = invoice_data['invoice_id']
            
            audit_record = {
                "invoice_data": invoice_data,  # Include the full invoice data
                "validation_result": {"score": validation_details["overall_score"]},  # Add validation_result for blockchain
                "status": status,
                "explanation": explanation,
                "validation_score": validation_details["overall_score"],
                "timestamp": datetime.now().isoformat(),
                "validation_stages": validation_details,
                "issues_count": len(issues),
                "agent_decision": "automated_approval" if status == "approved" else ("conditional_approval" if status == "approved_with_conditions" else "automated_rejection")
            }
            
            # Submit to real ICP canister (all invoices for audit trail)
            print(f"🔗 Submitting to ICP blockchain...")
            blockchain_result = blockchain.log_invoice(audit_record)
            print(f"🔗 Blockchain: {blockchain_result.get('message', 'Logged successfully')}")
            
        except Exception as e:
            print(f"❌ Blockchain logging failed: {e}")
            blockchain_result = {"success": False, "error": str(e)}
        
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
        
        # Always include blockchain result for transparency
        if blockchain_result:
            result["blockchain"] = blockchain_result
            result["blockchain_result"] = blockchain_result  # For compatibility
        
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
        
        print(f"📥 Received invoice submission via HTTP API")
        result = process_invoice(invoice_data)
        
        # Include blockchain result in response
        if 'blockchain' in result:
            result['blockchain_result'] = result['blockchain']
        
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
                "stats": "/stats",
                "chat_agent": "http://127.0.0.1:8002/submit"
            },
            "chat_integration": {
                "natural_language_queries": True,
                "privacy_protected": True,
                "supported_commands": [
                    "check invoice [ID]",
                    "fraud risk for [ID]", 
                    "show latest invoices",
                    "system statistics"
                ]
            }
        })
    except Exception as e:
        return jsonify({"error": str(e), "status": "unhealthy"}), 500

@app.route('/chat', methods=['POST'])
def chat_with_agent():
    """Chat endpoint for natural language queries with GPT integration and privacy protection"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({"error": "Message is required"}), 400
        
        message_lower = message.lower()
        response = ""
        
        # Extract invoice ID from message using regex
        import re
        invoice_id_pattern = r'(?:invoice\s+)?([A-Z]{2,4}[-_]?\d{3,4}[-_]?\d{3,4}|[A-Z]{3,6}[-_]?\d{3,6})'
        invoice_match = re.search(invoice_id_pattern, message, re.IGNORECASE)
        
        try:
            # Initialize blockchain integration for real data queries
            blockchain = BlockchainIntegration()
            context_data = {}
            
            # Gather context data for GPT
            if invoice_match:
                invoice_id = invoice_match.group(1).upper()
                print(f"🔍 Chat: Looking up invoice {invoice_id}")
                
                # Get specific invoice
                invoice_result = blockchain.get_invoice_by_id(invoice_id)
                
                if invoice_result and invoice_result.get("success"):
                    invoice = invoice_result["invoice"]
                    
                    # Create privacy-safe context for GPT
                    context_data = {
                        "type": "single_invoice",
                        "invoice_id": invoice.get('id', ''),
                        "status": invoice.get('status', 'unknown'),
                        "validation_score": invoice.get('validationScore', 0),
                        "risk_score": invoice.get('riskScore', 0),
                        "fraud_risk": invoice.get('fraudRisk', 'unknown'),
                        "amount": invoice.get('amount', 0),
                        "vendor_name": invoice.get('vendor_name', ''),  # Safe to include vendor name
                        "date": invoice.get('date', ''),
                        "timestamp": invoice.get('timestamp', 0)
                    }
                else:
                    context_data = {
                        "type": "invoice_not_found",
                        "requested_id": invoice_id
                    }
            
            # System stats queries
            elif 'statistics' in message_lower or 'stats' in message_lower or 'total' in message_lower or 'count' in message_lower:
                all_invoices_result = blockchain.get_all_invoices()
                
                if all_invoices_result and all_invoices_result.get("success"):
                    invoices = all_invoices_result["invoices"]
                    
                    # Calculate privacy-safe aggregate stats
                    approved_count = sum(1 for inv in invoices if inv.get('status', '').lower() == 'approved')
                    high_risk_count = sum(1 for inv in invoices if inv.get('fraudRisk', '') == 'HIGH')
                    avg_validation_score = sum(inv.get('validationScore', 0) for inv in invoices) / len(invoices) if invoices else 0
                    
                    context_data = {
                        "type": "system_stats",
                        "total_invoices": len(invoices),
                        "approved_count": approved_count,
                        "high_risk_count": high_risk_count,
                        "avg_validation_score": round(avg_validation_score, 1),
                        "approval_rate": round(approved_count/len(invoices)*100, 1) if invoices else 0,
                        "high_risk_rate": round(high_risk_count/len(invoices)*100, 1) if invoices else 0
                    }
            
            # Recent invoices query
            elif 'recent' in message_lower or 'latest' in message_lower or 'last' in message_lower:
                all_invoices_result = blockchain.get_all_invoices()
                
                if all_invoices_result and all_invoices_result.get("success"):
                    invoices = all_invoices_result["invoices"]
                    # Sort by timestamp (most recent first)
                    recent_invoices = sorted(invoices, key=lambda x: x.get('timestamp', 0), reverse=True)[:5]
                    
                    # Create privacy-safe summary
                    recent_summary = []
                    for inv in recent_invoices:
                        recent_summary.append({
                            "id": inv.get('id', ''),
                            "status": inv.get('status', ''),
                            "fraud_risk": inv.get('fraudRisk', ''),
                            "validation_score": inv.get('validationScore', 0),
                            "vendor_name": inv.get('vendor_name', ''),  # Safe to include
                            "amount": inv.get('amount', 0)
                        })
                    
                    context_data = {
                        "type": "recent_invoices",
                        "invoices": recent_summary
                    }
            
            # Use GPT to generate intelligent response
            if context_data:
                response = generate_gpt_response(message, context_data)
            else:
                # For general queries, try to get system overview and use GPT
                print("🧠 General query detected, gathering system context for GPT")
                try:
                    all_invoices_result = blockchain.get_all_invoices()
                    
                    if all_invoices_result and all_invoices_result.get("success"):
                        invoices = all_invoices_result["invoices"]
                        
                        # Calculate comprehensive system stats
                        approved_count = sum(1 for inv in invoices if inv.get('status', '').lower() == 'approved')
                        rejected_count = sum(1 for inv in invoices if inv.get('status', '').lower() == 'rejected')
                        high_risk_count = sum(1 for inv in invoices if inv.get('fraudRisk', '') == 'HIGH')
                        medium_risk_count = sum(1 for inv in invoices if inv.get('fraudRisk', '') == 'MEDIUM')
                        avg_validation_score = sum(inv.get('validationScore', 0) for inv in invoices) / len(invoices) if invoices else 0
                        
                        # Find problematic invoices for "worry about" queries
                        problematic_invoices = [
                            inv for inv in invoices 
                            if inv.get('fraudRisk', '') in ['HIGH', 'MEDIUM'] or 
                               inv.get('validationScore', 0) < 70 or
                               inv.get('status', '').lower() == 'rejected'
                        ]
                        
                        context_data = {
                            "type": "general_system_query",
                            "total_invoices": len(invoices),
                            "approved_count": approved_count,
                            "rejected_count": rejected_count,
                            "high_risk_count": high_risk_count,
                            "medium_risk_count": medium_risk_count,
                            "problematic_count": len(problematic_invoices),
                            "avg_validation_score": round(avg_validation_score, 1),
                            "approval_rate": round(approved_count/len(invoices)*100, 1) if invoices else 0,
                            "high_risk_rate": round(high_risk_count/len(invoices)*100, 1) if invoices else 0,
                            "user_query_intent": message_lower  # Help GPT understand what user is asking about
                        }
                        
                        response = generate_gpt_response(message, context_data)
                    else:
                        response = generate_gpt_response(message, {"type": "no_data", "user_query_intent": message_lower})
                except Exception as e:
                    print(f"Error gathering system context: {e}")
                    response = generate_basic_response(message_lower)
                    
        except Exception as blockchain_error:
            print(f"❌ Blockchain query error: {blockchain_error}")
            # Generate helpful response even if blockchain fails
            response = generate_basic_response(message_lower)
        
        return jsonify({
            "data": {
                "reply": response
            },
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "query": message[:100] + "..." if len(message) > 100 else message
        })
        
    except Exception as e:
        print(f"❌ Chat endpoint error: {e}")
        return jsonify({
            "data": {
                "reply": f"Sorry, I encountered an error processing your request: {str(e)}. Please try again."
            },
            "success": False
        }), 400

def generate_gpt_response(user_message: str, context_data: dict) -> str:
    """Generate intelligent response using GPT with privacy-protected data"""
    try:
        from utils.openai_explain import get_openai_client
        
        client = get_openai_client()
        if not client:
            return generate_fallback_response(user_message, context_data)
        
        # Create system prompt for invoice assistant
        system_prompt = """You are an intelligent Invoice Chain Agent assistant. You help users understand their invoice validation system, analyze risks, and provide insights.

Key capabilities:
- Analyze invoice validation status and risk scores
- Explain fraud detection results
- Provide system statistics and trends
- Answer questions about invoice processing

Guidelines:
- Be conversational and helpful
- Use emojis appropriately (📊 for stats, ✅ for approved, ⚠️ for risks, etc.)
- Keep responses concise but informative
- Focus on the specific data provided in context
- Never make up data - only use the provided context
- Maintain privacy - sensitive details are already filtered out"""

        # Create context-aware user prompt
        if context_data["type"] == "single_invoice":
            if "invoice_not_found" in context_data.get("type", ""):
                context_prompt = f"The user asked about invoice {context_data['requested_id']} but it was not found in the system."
            else:
                inv = context_data
                context_prompt = f"""The user is asking about invoice {inv['invoice_id']}:
- Status: {inv['status']}
- Validation Score: {inv['validation_score']}/100
- Risk Score: {inv['risk_score']}/100  
- Fraud Risk Level: {inv['fraud_risk']}
- Vendor: {inv['vendor_name']}
- Amount: ${inv['amount']:,.2f}
- Date: {inv['date']}"""

        elif context_data["type"] == "system_stats":
            stats = context_data
            context_prompt = f"""System statistics:
- Total Invoices: {stats['total_invoices']}
- Approved: {stats['approved_count']} ({stats['approval_rate']}%)
- High Risk: {stats['high_risk_count']} ({stats['high_risk_rate']}%)
- Average Validation Score: {stats['avg_validation_score']}/100"""

        elif context_data["type"] == "recent_invoices":
            recent = context_data['invoices']
            context_prompt = f"Recent invoices ({len(recent)} most recent):\n"
            for i, inv in enumerate(recent, 1):
                context_prompt += f"{i}. {inv['id']} - {inv['vendor_name']} (${inv['amount']:,.2f}) - {inv['status']} - {inv['fraud_risk']} risk\n"

        elif context_data["type"] == "general_system_query":
            stats = context_data
            context_prompt = f"""System overview for general inquiry:
- Total Invoices: {stats['total_invoices']}
- Approved: {stats['approved_count']} ({stats['approval_rate']}%)
- Rejected: {stats['rejected_count']}
- High Risk: {stats['high_risk_count']} ({stats['high_risk_rate']}%)
- Medium Risk: {stats['medium_risk_count']}
- Problematic Invoices: {stats['problematic_count']} (requiring attention)
- Average Validation Score: {stats['avg_validation_score']}/100

User's original question intent: "{stats['user_query_intent']}" """

        elif context_data["type"] == "no_data":
            context_prompt = f"No invoice data available yet in the system. User asked: \"{context_data['user_query_intent']}\""

        else:
            context_prompt = "General invoice system inquiry."

        # Generate response
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context: {context_prompt}\n\nUser question: {user_message}"}
        ]

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=300,
            temperature=0.7
        )

        gpt_response = response.choices[0].message.content.strip()
        print(f"🤖 GPT Response generated: {len(gpt_response)} chars")
        return gpt_response

    except Exception as e:
        print(f"❌ GPT generation failed: {e}")
        return generate_fallback_response(user_message, context_data)

def generate_fallback_response(user_message: str, context_data: dict) -> str:
    """Generate structured response when GPT is unavailable"""
    if context_data["type"] == "single_invoice":
        inv = context_data
        if inv['status'] == 'approved':
            return f"✅ **Invoice {inv['invoice_id']} Status:** APPROVED\n\n• Vendor: {inv['vendor_name']}\n• Amount: ${inv['amount']:,.2f}\n• Risk Level: {inv['fraud_risk']}\n• Validation Score: {inv['validation_score']}/100"
        else:
            return f"⚠️ **Invoice {inv['invoice_id']} Status:** {inv['status'].upper()}\n\n• Vendor: {inv['vendor_name']}\n• Amount: ${inv['amount']:,.2f}\n• Risk Level: {inv['fraud_risk']}\n• Validation Score: {inv['validation_score']}/100"
    
    elif context_data["type"] == "system_stats":
        stats = context_data
        return f"📊 **System Statistics:**\n\n• Total Invoices: {stats['total_invoices']}\n• Approved: {stats['approved_count']} ({stats['approval_rate']}%)\n• High Risk: {stats['high_risk_count']} ({stats['high_risk_rate']}%)\n• Average Score: {stats['avg_validation_score']}/100"
    
    elif context_data["type"] == "recent_invoices":
        response = "📋 **Recent Invoices:**\n\n"
        for i, inv in enumerate(context_data['invoices'], 1):
            status_emoji = "✅" if inv['status'] == 'approved' else "⚠️"
            response += f"{i}. {status_emoji} {inv['id']} - {inv['vendor_name']} (${inv['amount']:,.2f})\n"
        return response
    
    return generate_basic_response(user_message.lower())

def generate_basic_response(message_lower: str) -> str:
    """Generate basic response patterns"""
    if 'hello' in message_lower or 'hi' in message_lower:
        return "👋 Hello! I'm your Invoice Chain Agent. Ask me about specific invoices, system statistics, or recent activity!"
    elif 'help' in message_lower:
        return "🤖 I can help you with:\n• **Invoice Status**: 'What's the status of invoice INV-001?'\n• **Risk Analysis**: 'What's the risk of invoice ABC-123?'\n• **System Stats**: 'Show me statistics'\n• **Recent Activity**: 'Show recent invoices'"
    elif 'fraud' in message_lower:
        return "🔍 **Fraud Detection System:**\nOur AI uses multi-layer analysis:\n• OCR validation\n• Vendor verification\n• Pattern recognition\n• Risk scoring algorithms\n\nAsk about specific invoices for detailed analysis!"
    else:
        return f"🤖 I can help you with invoice queries! Try asking:\n• 'Status of invoice INV-001'\n• 'Show system statistics'\n• 'What are recent invoices?'\n\nFor specific invoices, use the exact ID format."

@app.route('/invoices', methods=['GET'])
def get_all_invoices():
    """Get all invoices from blockchain for audit logs page"""
    try:
        # Import blockchain integration from root directory
        import sys
        import os
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sys.path.insert(0, root_dir)
        from blockchain.integration import BlockchainIntegration
        
        # Initialize blockchain integration
        blockchain = BlockchainIntegration()
        
        # Get invoices from ICP canister
        result = blockchain.get_all_invoices()
        
        if result.get("success"):
            invoices = result.get("invoices", [])
            
            # Convert to frontend format
            formatted_invoices = []
            for invoice in invoices:
                formatted_invoices.append({
                    "id": invoice.get("id", ""),
                    "status": invoice.get("status", "unknown"),
                    "validationScore": invoice.get("validationScore", 0),
                    "riskScore": invoice.get("riskScore", 0),
                    "fraudRisk": invoice.get("fraudRisk", "unknown"),
                    "timestamp": invoice.get("timestamp", 0),
                    "vendor_name": invoice.get("vendor_name", ""),
                    "amount": invoice.get("amount", 0.0)
                })
            
            return jsonify({
                "data": formatted_invoices,
                "total": len(formatted_invoices),
                "source": result.get("source", "icp_canister"),
                "message": "Retrieved from ICP blockchain"
            })
        else:
            # No fallback - return actual error from canister
            print(f"❌ Canister query failed: {result.get('error', 'Unknown error')}")
            
            return jsonify({
                "error": result.get('error', 'Failed to retrieve invoices from ICP canister'),
                "data": [],
                "total": 0,
                "source": "icp_canister_error",
                "message": "ICP canister connection failed"
            }), 500
    except Exception as e:
        print(f"❌ Error in /invoices endpoint: {e}")
        return jsonify({"error": str(e), "data": []}), 500

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
        
        # Check if user wants AI processing (privacy-aware OCR)
        use_ai = request.form.get('use_ai', 'true').lower() == 'true'  # Default to enabled
        print(f"🤖 AI processing: {'enabled' if use_ai else 'disabled'} (privacy protection active)")
        
        # Process the uploaded image with OCR
        ocr_result = process_uploaded_invoice(file, use_ai=use_ai)
        
        print(f"🔄 OCR result: {ocr_result}")
        
        if not ocr_result['success']:
            print(f"❌ OCR failed: {ocr_result['error']}")
            return jsonify(ocr_result), 400
        
        response_data = {
            "success": True,
            "extracted_text": ocr_result['extracted_text'],
            "invoice_data": ocr_result['invoice_data'],
            "confidence": ocr_result['confidence'],
            "extraction_method": ocr_result.get('extraction_method', 'OCR'),
            "privacy_protected": ocr_result.get('privacy_protected', False),
            "message": "Invoice data extracted successfully. Review and edit before submitting for validation.",
            "next_step": "Submit extracted data to /submit endpoint for full enterprise validation",
            "chat_agent_hint": "💬 Try chatting with our AI: 'check invoice [ID]' for status queries!"
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