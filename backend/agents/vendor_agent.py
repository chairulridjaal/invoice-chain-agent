from uagents import Agent, Context, Protocol, Model
import asyncio
import json
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Define message schema (same as invoice_agent)
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

# Vendor agent that simulates sending invoices
vendor_agent = Agent(name="vendor", seed="vendor-secret-seed", port=8003)

# Define protocol
vendor_protocol = Protocol(name="vendor_protocol")

# Sample invoices to send
sample_invoices = [
    {
        "invoice_id": "INV-001",
        "vendor_name": "Acme Corp",
        "tax_id": "123456789",
        "amount": 1500.00,
        "date": "2025-08-03"
    },
    {
        "invoice_id": "INV-002",
        "vendor_name": "Tech Solutions Inc",
        "tax_id": "987654321",
        "amount": 2750.50,
        "date": "2025-08-03"
    },
    {
        "invoice_id": "INV-003",
        "vendor_name": "Bad Invoice Co",
        "tax_id": "",  # Missing tax ID - should be rejected
        "amount": -100.00,  # Invalid amount
        "date": "2025-08-03"
    }
]

@vendor_agent.on_event("startup")
async def send_invoices(ctx: Context):
    """Send sample invoices to the invoice agent"""
    await asyncio.sleep(3)  # Wait for other agents to start
    
    ctx.logger.info("🏢 Vendor agent starting to send invoices...")
    
    for invoice_data in sample_invoices:
        invoice = Invoice(**invoice_data)
        ctx.logger.info(f"📤 Sending invoice: {invoice.invoice_id}")
        
        try:
            # Try agent-to-agent communication first
            await ctx.send(
                "agent1q22r40w47rp55ql7uzlhrnqs0v9h3cceafsl9ylfcu3583gsnma9y9c2s7s",
                invoice
            )
            ctx.logger.info(f"✅ Invoice {invoice.invoice_id} sent via agent")
        except Exception as e:
            ctx.logger.error(f"❌ Agent send failed: {e}")
            # Fallback to HTTP
            try:
                import requests
                response = requests.post("http://127.0.0.1:8001/submit", json=invoice.dict())
                ctx.logger.info(f"✅ Invoice {invoice.invoice_id} sent via HTTP: {response.json()}")
            except Exception as http_error:
                ctx.logger.error(f"❌ HTTP fallback failed: {http_error}")
        
        await asyncio.sleep(2)

@vendor_protocol.on_message(model=Explanation)
async def handle_response(ctx: Context, sender: str, msg: Explanation):
    """Handle responses from the invoice agent"""
    ctx.logger.info(f"📬 Received response for {msg.invoice_id}:")
    ctx.logger.info(f"Status: {msg.status}")
    ctx.logger.info(f"Explanation: {msg.explanation}")

vendor_agent.include(vendor_protocol)

if __name__ == "__main__":
    vendor_agent.run()
