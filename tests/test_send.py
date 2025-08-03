from uagents import Agent, Context, Model, Protocol
from agents.invoice_agent import Invoice, Explanation

# Setup test agent
test_agent = Agent(name="tester", seed="tester-seed-123", port=8002)

# Define protocol
protocol = Protocol(name="invoice_protocol")

@test_agent.on_event("startup")
async def send_invoice(ctx: Context):
    # Wait a bit for the agent to be ready
    import asyncio
    await asyncio.sleep(2)
    
    invoice = Invoice(
        invoice_id="INV-002",
        vendor_name="Stark Industries",
        tax_id="1234567890",
        amount=1200.75,
        date="2025-08-03"
    )

    ctx.logger.info("📤 Sending invoice...")
    try:
        await ctx.send(
            "agent1q22r40w47rp55ql7uzlhrnqs0v9h3cceafsl9ylfcu3583gsnma9y9c2s7s",
            invoice
        )
        ctx.logger.info("✅ Invoice sent successfully!")
    except Exception as e:
        ctx.logger.error(f"❌ Failed to send invoice: {e}")
        # Try HTTP endpoint as fallback
        import requests
        try:
            response = requests.post("http://127.0.0.1:8001/submit", json=invoice.dict())
            ctx.logger.info(f"✅ HTTP fallback successful: {response.json()}")
        except Exception as http_error:
            ctx.logger.error(f"❌ HTTP fallback also failed: {http_error}")

@protocol.on_message(model=Explanation)
async def handle_response(ctx: Context, sender: str, msg: Explanation):
    ctx.logger.info(f"✅ Got explanation for {msg.invoice_id}:")
    ctx.logger.info(f"Status: {msg.status}")
    ctx.logger.info(f"{msg.explanation}")

test_agent.include(protocol)

if __name__ == "__main__":
    test_agent.run()
