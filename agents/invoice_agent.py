from uagents import Agent, Context, Protocol, Model
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.openai_explain import explain_validation
import json
import asyncio
from threading import Thread
from flask import Flask, request, jsonify

# Define message schema
class Invoice(Model):
    invoice_id: str
    vendor_name: str
    tax_id: str
    amount: float
    date: str

class Explanation(Model):
    invoice_id: str
    status: str
    explanation: str

# Define agent
invoice_agent = Agent(
    name="invoice_chain_agent",
    seed="invoice_chain_agent_secret_phrase",
    port=8000
)

# Define protocol
invoice_protocol = Protocol(name="invoice_protocol")

def process_invoice(invoice_data):
    """Process invoice and return result"""
    # Basic validation
    issues = []
    if not invoice_data.get("tax_id"):
        issues.append("Missing tax ID")
    if invoice_data.get("amount", 0) <= 0:
        issues.append("Invalid amount")

    status = "approved" if not issues else "rejected"
    explanation = explain_validation(invoice_data, issues)
    
    print(f"Invoice {invoice_data['invoice_id']} - {status.upper()} - {explanation}")
    
    return {
        "invoice_id": invoice_data["invoice_id"],
        "status": status,
        "explanation": explanation
    }

@invoice_protocol.on_message(model=Invoice)
async def handle_invoice(ctx: Context, sender: str, msg: Invoice):
    ctx.logger.info(f"Received invoice: {msg.invoice_id}")
    result = process_invoice(msg.dict())
    ctx.logger.info(f"Invoice {result['invoice_id']} - {result['status'].upper()} - {result['explanation']}")
    await ctx.send(sender, Explanation(**result))


# Simple Flask app for HTTP endpoint
app = Flask(__name__)

@app.route('/submit', methods=['POST'])
def submit_invoice():
    try:
        invoice_data = request.get_json()
        result = process_invoice(invoice_data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

def run_flask():
    app.run(host='127.0.0.1', port=8001, debug=False)

invoice_agent.include(invoice_protocol)

if __name__ == "__main__":
    # Start Flask in a separate thread
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    print("Starting invoice agent...")
    print("HTTP endpoint available at: http://127.0.0.1:8001/submit")
    
    # Start the agent
    invoice_agent.run()