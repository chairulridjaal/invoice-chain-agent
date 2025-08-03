from uagents import Agent, Context, Model, Protocol
from agents.invoice_agent import Invoice, Explanation

# Setup test agent
test_agent = Agent(name="tester", seed="tester-seed-123", port=8001)

# Define protocol
protocol = Protocol(name="invoice_protocol")

@test_agent.on_event("startup")
async def send_invoice(ctx: Context):
    invoice = Invoice(
        invoice_id="INV-002",
        vendor_name="Stark Industries",
        tax_id="1234567890",
        amount=1200.75,
        date="2025-08-03"
    )

    ctx.logger.info("📤 Sending invoice...")
    await ctx.send(
        "agent1q0zrfk8mkc3rduvlrp8zyrnpxflknt6e5tququ58j8fgscy07l66x9enpkz@127.0.0.1:8000",
        invoice
    )

@protocol.on_message(model=Explanation)
async def handle_response(ctx: Context, sender: str, msg: Explanation):
    ctx.logger.info(f"✅ Got explanation for {msg.invoice_id}:")
    ctx.logger.info(f"Status: {msg.status}")
    ctx.logger.info(f"{msg.explanation}")

test_agent.include(protocol)

if __name__ == "__main__":
    test_agent.run()
