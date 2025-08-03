from uagents import Agent, Context, Protocol
import asyncio
import sys
import os
import requests

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from blockchain.integration import BlockchainIntegration

# Audit agent that monitors and queries the blockchain
audit_agent = Agent(name="auditor", seed="audit-secret-seed", port=8004)

# Define protocol
audit_protocol = Protocol(name="audit_protocol")

# Initialize blockchain integration
blockchain = BlockchainIntegration()

@audit_agent.on_event("startup")
async def start_audit_monitoring(ctx: Context):
    """Start monitoring and auditing invoices"""
    await asyncio.sleep(5)  # Wait for other agents to process some invoices
    
    ctx.logger.info("🔍 Audit agent starting monitoring...")
    
    while True:
        try:
            # Get statistics from the ICP canister
            stats_result = await blockchain.get_stats()
            
            if stats_result["success"]:
                ctx.logger.info("📊 Invoice Statistics:")
                ctx.logger.info(f"Stats: {stats_result.get('stats', 'No stats available')}")
            else:
                ctx.logger.error(f"❌ Failed to get stats: {stats_result.get('error', 'Unknown error')}")
            
            # Check health of the system
            health_result = await blockchain.health_check()
            
            if health_result["success"]:
                ctx.logger.info(f"💚 System Health: {health_result.get('health', 'Unknown')}")
            else:
                ctx.logger.warning(f"⚠️ Health check failed: {health_result.get('error', 'Unknown error')}")
            
            # Try to get audit logs for recent invoices
            test_invoice_ids = ["INV-001", "INV-002", "INV-003"]
            
            for invoice_id in test_invoice_ids:
                try:
                    audit_logs = await blockchain.get_audit_logs(invoice_id)
                    if audit_logs["success"]:
                        ctx.logger.info(f"📋 Audit logs for {invoice_id}: Found logs")
                    else:
                        ctx.logger.info(f"📋 No audit logs found for {invoice_id}")
                except Exception as e:
                    ctx.logger.error(f"❌ Error getting audit logs for {invoice_id}: {e}")
            
        except Exception as e:
            ctx.logger.error(f"❌ Error in audit monitoring: {e}")
        
        # Wait before next audit cycle
        await asyncio.sleep(30)  # Audit every 30 seconds

@audit_agent.on_event("shutdown")
async def audit_shutdown(ctx: Context):
    """Generate final audit report on shutdown"""
    ctx.logger.info("📄 Generating final audit report...")
    
    try:
        # Get final statistics
        stats_result = await blockchain.get_stats()
        
        if stats_result["success"]:
            ctx.logger.info("📊 Final Audit Report:")
            ctx.logger.info(f"Statistics: {stats_result.get('stats', 'No stats')}")
        
        # Try to get HTTP endpoint stats
        try:
            response = requests.get("http://127.0.0.1:8001/stats", timeout=5)
            ctx.logger.info(f"🌐 HTTP Stats: {response.json()}")
        except:
            ctx.logger.info("🌐 HTTP endpoint unavailable")
        
    except Exception as e:
        ctx.logger.error(f"❌ Error generating final report: {e}")

audit_agent.include(audit_protocol)

if __name__ == "__main__":
    audit_agent.run()
