"""
Invoice Chain Agent - Chat Interface for Agentverse/ASI:One
Hackathon: Fetch.ai & Internet Computer NextGen Agents 2025

This agent implements the official Fetch.ai uAgent Chat Protocol for Agentverse integration.
Provides intelligent invoice validation queries with GPT integration and ICP blockchain data.

Privacy-First: Only returns metadata (ID, status, score) - never sensitive content.
"""

from uagents import Agent, Context, Protocol, Model, Bureau
from uagents.setup import fund_agent_if_low
import os
import sys
import re
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Add project paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from blockchain.integration import BlockchainIntegration
from utils.invoice_validator import InvoiceValidator

# Add GPT integration for intelligent responses
try:
    from utils.openai_explain import get_openai_client
    GPT_AVAILABLE = True
    print("✅ GPT integration available")
except ImportError:
    GPT_AVAILABLE = False
    print("⚠️ GPT integration not available")

# Official uAgent Chat Protocol Message Models
class InvoiceQueryMessage(Model):
    """Request message for invoice queries following uAgent Protocol"""
    text: str
    query_type: str = "general"  # general, invoice_check, fraud_analysis, system_stats
    invoice_id: Optional[str] = None
    sender_address: Optional[str] = None

class InvoiceResponseMessage(Model):
    """Response message for invoice queries following uAgent Protocol"""
    text: str
    success: bool = True
    query_type: str = "general"
    metadata: Optional[Dict] = None
    timestamp: str = ""

# Initialize Invoice Chain Chat Agent for Agentverse
invoice_chat_agent = Agent(
    name="InvoiceChainChatAgent",
    seed="invoice_chain_hackathon_2025_fetch_icp_agentverse",
    port=8002,
    endpoint=["http://127.0.0.1:8002/submit"]
)

# Fund agent for testnet operations
fund_agent_if_low(invoice_chat_agent.wallet.address())

print(f"🤖 Invoice Chat Agent Address: {invoice_chat_agent.address}")
print(f"💰 Agent Wallet: {invoice_chat_agent.wallet.address()}")

# Initialize blockchain integration
blockchain = BlockchainIntegration()
validator = InvoiceValidator()

# Official uAgent Chat Protocol for Invoice Chain
invoice_chat_protocol = Protocol(name="InvoiceChainChatProtocol", version="1.0.0")

class ChatIntent:
    """Parse user intents from natural language"""
    
    @staticmethod
    def extract_invoice_id(message: str) -> Optional[str]:
        """Extract invoice ID from user message"""
        patterns = [
            r'invoice[:\s]+([A-Z0-9\-_]+)',
            r'inv[:\s]+([A-Z0-9\-_]+)', 
            r'id[:\s]+([A-Z0-9\-_]+)',
            r'([A-Z]{2,}[-_]\d+)',  
            r'([A-Z]+\d+[A-Z]*)', 
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).upper()
        return None
    
    @staticmethod
    def determine_intent(message: str) -> str:
        """Determine user intent from message"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['check', 'status', 'lookup', 'find', 'get']):
            return "check_invoice"
        elif any(word in message_lower for word in ['fraud', 'risk', 'suspicious', 'security']):
            return "fraud_analysis" 
        elif any(word in message_lower for word in ['latest', 'recent', 'last', 'list']):
            return "list_invoices"
        elif any(word in message_lower for word in ['stats', 'statistics', 'summary', 'overview']):
            return "system_stats"
        elif any(word in message_lower for word in ['help', 'commands', 'what can']):
            return "help"
        else:
            return "general_query"

class InvoiceQueryHandler:
    """Handle different types of invoice queries with privacy protection"""
    
    def __init__(self, blockchain: BlockchainIntegration):
        self.blockchain = blockchain
    
    async def check_invoice_status(self, invoice_id: str) -> str:
        """Check specific invoice status - privacy protected"""
        try:
            # Query ICP canister for invoice metadata only
            result = self.blockchain.get_invoice_by_id(invoice_id)
            
            if result.get("success") and result.get("invoice"):
                invoice = result["invoice"]
                
                # Extract safe metadata only
                status = invoice.get("status", "unknown")
                validation_score = invoice.get("validationScore", 0)
                risk_score = invoice.get("riskScore", 0)
                fraud_risk = invoice.get("fraudRisk", "UNKNOWN")
                timestamp = invoice.get("timestamp", 0)
                
                # Format privacy-safe response
                return f"""✅ **Invoice {invoice_id}** found on ICP blockchain:

**Status:** {status.upper().replace('_', ' ')}
**Validation Score:** {validation_score}/100
**Risk Score:** {risk_score}/100
**Fraud Risk:** {fraud_risk}
**Processed:** {self._format_timestamp(timestamp)}
**Blockchain:** Verified on Internet Computer

💡 All sensitive data remains encrypted on-chain."""
            else:
                return f"""❌ **Invoice {invoice_id}** not found in ICP canister.

Possible reasons:
• Invoice not yet processed
• Invalid invoice ID
• Still in validation pipeline

💡 Try checking recent submissions or contact system admin."""
                
        except Exception as e:
            return f"⚠️ Error querying blockchain: Unable to retrieve invoice status at this time."
    
    async def fraud_analysis(self, invoice_id: str) -> str:
        """Provide fraud risk analysis - privacy protected"""
        try:
            result = self.blockchain.get_invoice_by_id(invoice_id)
            
            if result.get("success") and result.get("invoice"):
                invoice = result["invoice"]
                fraud_risk = invoice.get("fraudRisk", "UNKNOWN")
                status = invoice.get("status", "unknown")
                risk_score = invoice.get("riskScore", 0)
                validation_score = invoice.get("validationScore", 0)
                
                fraud_indicators = self._get_fraud_indicators(fraud_risk, risk_score, validation_score)
                
                return f"""🔍 **Fraud Analysis for {invoice_id}:**

**Risk Level:** {fraud_risk}
**Risk Score:** {risk_score}/100
**Overall Status:** {status.upper().replace('_', ' ')}

**Security Indicators:**
{fraud_indicators}

🛡️ **Privacy Note:** Detailed analysis available to authorized personnel only.
📊 **Validation Pipeline:** 4-stage enterprise security validation completed."""
            else:
                return f"❌ Cannot analyze {invoice_id} - invoice not found in blockchain."
                
        except Exception as e:
            return f"⚠️ Fraud analysis unavailable: System temporarily unreachable."
    
    async def list_recent_invoices(self, limit: int = 5) -> str:
        """List recent invoices - metadata only"""
        try:
            result = self.blockchain.get_all_invoices()
            
            if result.get("success") and result.get("invoices"):
                invoices = result["invoices"]
                
                # Sort by timestamp and limit
                sorted_invoices = sorted(invoices, key=lambda x: x.get("timestamp", 0), reverse=True)
                recent = sorted_invoices[:limit]
                
                if not recent:
                    return "📭 No invoices found in ICP canister yet."
                
                invoice_list = []
                for inv in recent:
                    invoice_id = inv.get("id", "Unknown")
                    status = inv.get("status", "unknown")
                    validation_score = inv.get("validationScore", 0)
                    fraud_risk = inv.get("fraudRisk", "UNKNOWN")
                    
                    invoice_list.append(f"• **{invoice_id}** - {status.upper().replace('_', ' ')} ({validation_score}/100) - Risk: {fraud_risk}")
                
                return f"""📋 **Recent Invoices on ICP Blockchain:**

{chr(10).join(invoice_list)}

💡 Use "check invoice [ID]" for detailed status.
🔒 Sensitive data protected by enterprise encryption."""
            else:
                return "📭 No invoices found on ICP blockchain yet."
                
        except Exception as e:
            return "⚠️ Unable to retrieve invoice list from blockchain."
    
    async def system_statistics(self) -> str:
        """Get system-wide statistics"""
        try:
            result = self.blockchain.get_all_invoices()
            
            if result.get("success") and result.get("invoices"):
                invoices = result["invoices"]
                
                # Calculate statistics
                total = len(invoices)
                approved = len([i for i in invoices if i.get("status") == "approved"])
                rejected = len([i for i in invoices if i.get("status") == "rejected"])
                conditional = len([i for i in invoices if i.get("status") == "approved_with_conditions"])
                
                avg_score = sum(i.get("validationScore", 0) for i in invoices) / total if total > 0 else 0
                high_risk = len([i for i in invoices if i.get("fraudRisk") == "HIGH"])
                
                return f"""📊 **Invoice Chain Agent Statistics:**

**Total Processed:** {total} invoices
**✅ Approved:** {approved} ({approved/total*100:.1f}%)
**⚠️ Conditional:** {conditional} ({conditional/total*100:.1f}%)
**❌ Rejected:** {rejected} ({rejected/total*100:.1f}%)

**Quality Metrics:**
• Average Validation Score: {avg_score:.1f}/100
• High Risk Detected: {high_risk} cases
• Blockchain Storage: Internet Computer (ICP)

**Pipeline Performance:**
• OCR Processing: Tesseract + GPT-4o-mini
• Validation Stages: 4-layer enterprise security
• Privacy Protection: ✅ Active
• Fraud Detection: ✅ Real-time"""
            else:
                return """📊 **System Status:**

**Status:** ✅ Online and Ready
**Blockchain:** Internet Computer (ICP) 
**Pipeline:** 4-stage validation active
**Privacy:** ✅ Fully protected
**OCR:** Tesseract + GPT-4o-mini ready

💡 No invoices processed yet. Upload your first invoice to get started!"""
                
        except Exception as e:
            return "⚠️ Unable to retrieve system statistics."
    
    def _get_fraud_indicators(self, fraud_risk: str, risk_score: int, validation_score: int) -> str:
        """Get fraud risk indicators without exposing sensitive data"""
        if fraud_risk == "LOW":
            return """• ✅ Vendor verification passed
• ✅ Amount within normal range  
• ✅ No suspicious patterns detected
• ✅ All validation stages passed"""
        elif fraud_risk == "MEDIUM":
            return """• ⚠️ Some validation flags raised
• ⚠️ Manual review recommended
• ✅ No critical security issues
• ✅ Vendor generally trusted"""
        else:  # HIGH or UNKNOWN
            return """• 🚨 Multiple risk factors detected
• 🚨 Manual intervention required
• ❌ Failed critical validation checks
• 🔍 Under security review"""
    
    def _format_timestamp(self, timestamp) -> str:
        """Format timestamp for display"""
        try:
            if isinstance(timestamp, (int, float)):
                dt = datetime.fromtimestamp(timestamp / 1_000_000_000)  # Convert from nanoseconds
                return dt.strftime("%Y-%m-%d %H:%M UTC")
            else:
                return "Unknown time"
        except:
            return "Unknown time"

# Initialize query handler
query_handler = InvoiceQueryHandler(blockchain)

async def handle_general_query(user_message: str, invoice_id: Optional[str] = None) -> str:
    """Handle general conversational queries with GPT integration"""
    try:
        if not GPT_AVAILABLE:
            # Fallback for when GPT is not available
            if invoice_id:
                return await query_handler.check_invoice_status(invoice_id)
            else:
                return f"""💡 **I can help you with invoice queries!**

I didn't understand "{user_message[:50]}..." 

Try these commands:
• "check invoice INV-123"
• "fraud analysis for GALT-009" 
• "show latest invoices"
• "system statistics"
• "help"

🔒 **Privacy Protected:** I only share metadata, never sensitive content."""

        # Get system context for intelligent responses
        try:
            result = blockchain.get_all_invoices()
            
            if result.get("success") and result.get("invoices"):
                invoices = result["invoices"]
                
                # Calculate system overview
                total = len(invoices)
                approved = len([i for i in invoices if i.get("status") == "approved"])
                rejected = len([i for i in invoices if i.get("status") == "rejected"])
                high_risk = len([i for i in invoices if i.get("fraudRisk") == "HIGH"])
                medium_risk = len([i for i in invoices if i.get("fraudRisk") == "MEDIUM"])
                avg_score = sum(i.get("validationScore", 0) for i in invoices) / total if total > 0 else 0
                
                # Find problematic invoices for "worry" queries
                problematic = [
                    inv for inv in invoices 
                    if inv.get("fraudRisk") in ["HIGH", "MEDIUM"] or 
                       inv.get("validationScore", 0) < 70 or
                       inv.get("status") == "rejected"
                ]
                
                context_data = {
                    "total_invoices": total,
                    "approved_count": approved,
                    "rejected_count": rejected,
                    "high_risk_count": high_risk,
                    "medium_risk_count": medium_risk,
                    "problematic_count": len(problematic),
                    "avg_validation_score": round(avg_score, 1),
                    "approval_rate": round(approved/total*100, 1) if total > 0 else 0,
                    "user_query": user_message.lower()
                }
                
                # Use GPT for intelligent response
                return await generate_intelligent_response(user_message, context_data, problematic[:3])
            else:
                return await generate_intelligent_response(user_message, {"total_invoices": 0, "user_query": user_message.lower()}, [])
                
        except Exception as e:
            print(f"Error getting system context: {e}")
            return await generate_intelligent_response(user_message, {"error": True, "user_query": user_message.lower()}, [])
            
    except Exception as e:
        print(f"Error in general query handler: {e}")
        return "⚠️ I'm having trouble processing your request right now. Please try a specific command like 'system stats' or 'check invoice [ID]'."

async def generate_intelligent_response(user_message: str, context: dict, problematic_invoices: list) -> str:
    """Generate intelligent conversational responses using GPT"""
    try:
        client = get_openai_client()
        if not client:
            return generate_fallback_response(user_message, context)
        
        # Create intelligent system prompt
        system_prompt = """You are an AI assistant for an Invoice Chain Agent system built on Internet Computer Protocol (ICP) blockchain. You help users understand their invoice validation system with conversational, intelligent responses.

Key capabilities:
- Answer questions about invoice system health and status
- Identify potential problems or risks
- Provide actionable insights about invoice processing
- Explain validation scores and fraud detection
- Give system overviews and trends

Guidelines:
- Be conversational and helpful, like a knowledgeable assistant
- Use appropriate emojis (📊 for stats, ⚠️ for warnings, ✅ for good news)
- Focus on the specific question the user asked
- Provide actionable insights when possible
- Keep responses concise but informative
- Always maintain privacy - sensitive invoice details are filtered out
- If asked about specific invoices by ID, suggest using "check invoice [ID]" command"""

        # Create context-aware prompt
        context_text = f"""Current System Context:
- Total Invoices: {context.get('total_invoices', 0)}
- Approved: {context.get('approved_count', 0)} ({context.get('approval_rate', 0)}%)
- Rejected: {context.get('rejected_count', 0)}
- High Risk: {context.get('high_risk_count', 0)}
- Medium Risk: {context.get('medium_risk_count', 0)}
- Problematic (need attention): {context.get('problematic_count', 0)}
- Average Validation Score: {context.get('avg_validation_score', 0)}/100

User's question: "{user_message}" """

        if problematic_invoices:
            context_text += f"\n\nProblematic invoices (privacy-safe metadata only):\n"
            for inv in problematic_invoices:
                context_text += f"- {inv.get('id', 'Unknown')}: {inv.get('status', 'unknown')} status, {inv.get('fraudRisk', 'unknown')} risk\n"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": context_text}
        ]

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=400,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"GPT generation error: {e}")
        return generate_fallback_response(user_message, context)

def generate_fallback_response(user_message: str, context: dict) -> str:
    """Generate fallback response when GPT is not available"""
    message_lower = user_message.lower()
    
    if any(word in message_lower for word in ['worry', 'problem', 'issue', 'concern', 'wrong']):
        if context.get('problematic_count', 0) > 0:
            return f"""⚠️ **System Alert:** {context['problematic_count']} invoices need attention out of {context['total_invoices']} total.

**Issues detected:**
• {context.get('high_risk_count', 0)} high-risk invoices
• {context.get('medium_risk_count', 0)} medium-risk invoices  
• {context.get('rejected_count', 0)} rejected invoices

💡 Use "list recent invoices" to see details or "check invoice [ID]" for specific analysis."""
        else:
            return f"""✅ **Good news!** Your invoice system looks healthy:

• {context.get('approved_count', 0)}/{context.get('total_invoices', 0)} invoices approved ({context.get('approval_rate', 0)}%)
• Average validation score: {context.get('avg_validation_score', 0)}/100  
• Low risk profile maintained

🚀 System running smoothly on ICP blockchain!"""
    
    elif any(word in message_lower for word in ['how', 'status', 'doing', 'health']):
        return f"""📊 **System Overview:**

• **Total Processed:** {context.get('total_invoices', 0)} invoices
• **Success Rate:** {context.get('approval_rate', 0)}% approved
• **Risk Status:** {context.get('high_risk_count', 0)} high-risk cases
• **Quality Score:** {context.get('avg_validation_score', 0)}/100 average

💡 Try "system stats" for detailed metrics or "show recent invoices" to browse."""
    
    else:
        return f"""💡 **I can help you with invoice queries!**

I didn't understand "{user_message[:50]}..." 

Try these commands:
• "Are there any invoices I need to worry about?"
• "How is my system doing?"
• "check invoice INV-123"
• "show system statistics"

🔒 **Privacy Protected:** I only share metadata, never sensitive content."""

# Official uAgent Protocol Message Handler
@invoice_chat_protocol.on_message(model=InvoiceQueryMessage, replies=InvoiceResponseMessage)
async def handle_invoice_query(ctx: Context, sender: str, msg: InvoiceQueryMessage):
    """Handle incoming invoice queries using official uAgent Chat Protocol"""
    
    ctx.logger.info(f"💬 Received query from {sender}: {msg.text}")
    
    try:
        # Parse query intent and extract invoice ID
        intent = ChatIntent.determine_intent(msg.text)
        invoice_id = ChatIntent.extract_invoice_id(msg.text)
        
        response_text = ""
        metadata = {}
        
        if intent == "check_invoice" and invoice_id:
            response_text = await query_handler.check_invoice_status(invoice_id)
            metadata = {"query_type": "invoice_check", "invoice_id": invoice_id}
            
        elif intent == "fraud_analysis" and invoice_id:
            response_text = await query_handler.fraud_analysis(invoice_id)
            metadata = {"query_type": "fraud_analysis", "invoice_id": invoice_id}
            
        elif intent == "fraud_analysis" and not invoice_id:
            response_text = """🔍 **Fraud Analysis Help:**

To analyze fraud risk, please specify an invoice ID:
• "fraud risk for INV-123"
• "check security of GALT-009"
• "is invoice ABC-456 suspicious?"

💡 All analysis maintains privacy - only metadata is shared."""
            metadata = {"query_type": "fraud_help"}
            
        elif intent == "list_invoices":
            # Extract number if specified
            numbers = re.findall(r'\b\d+\b', msg.text)
            limit = int(numbers[0]) if numbers else 5
            limit = min(limit, 20)  # Cap at 20 for performance
            response_text = await query_handler.list_recent_invoices(limit)
            metadata = {"query_type": "list_invoices", "limit": limit}
            
        elif intent == "system_stats":
            response_text = await query_handler.system_statistics()
            metadata = {"query_type": "system_stats"}
            
        elif intent == "help":
            response_text = """🤖 **Invoice Chain Agent Commands:**

**Query Invoices:**
• "check invoice INV-123" - Get invoice status
• "status of GALT-009" - Check validation result
• "fraud risk for ABC-456" - Security analysis

**List & Browse:**
• "show latest 5 invoices" - Recent submissions
• "list recent invoices" - Browse processed invoices

**System Info:**
• "system stats" - Overall statistics  
• "show statistics" - Performance metrics

**Privacy:** All responses protect sensitive data. Only metadata (ID, status, score) is shared.
**Blockchain:** Queries real ICP canister for verified data.

💡 Try: "check invoice [YOUR_ID]" or "show system stats" """
            metadata = {"query_type": "help"}

        else:
            # General query - use GPT for intelligent responses
            response_text = await handle_general_query(msg.text, invoice_id)
            metadata = {"query_type": "general", "gpt_enhanced": GPT_AVAILABLE}

        # Send structured response using official uAgent Protocol
        response = InvoiceResponseMessage(
            text=response_text,
            success=True,
            query_type=intent,
            metadata=metadata,
            timestamp=datetime.utcnow().isoformat()
        )
        
        await ctx.send(sender, response)
        ctx.logger.info(f"✅ Sent response to {sender}")
        
    except Exception as e:
        error_response = InvoiceResponseMessage(
            text=f"""⚠️ **System Error:** Unable to process your request at this time.

Please try again or contact system administrator.

**Error ID:** {str(e)[:20]}...""",
            success=False,
            query_type="error",
            metadata={"error": str(e)[:100]},
            timestamp=datetime.utcnow().isoformat()
        )
        
        await ctx.send(sender, error_response)
        ctx.logger.error(f"❌ Chat error: {e}")

# Include the protocol in the agent
invoice_chat_agent.include(invoice_chat_protocol, publish_manifest=True)

if __name__ == "__main__":
    print("🚀 Starting Official Fetch.ai Invoice Chain Chat Agent")
    print("=" * 70)
    print("🎯 Hackathon: Fetch.ai & Internet Computer NextGen Agents 2025")
    print("🔗 Blockchain: Internet Computer Protocol (ICP)")
    print("🤖 Framework: Official Fetch.ai uAgent Chat Protocol")
    print("🛡️ Privacy: Metadata only - sensitive data protected")
    print("🧠 AI: GPT-powered conversational intelligence")
    print("📜 Manifest: Published to Almanac for Agentverse discovery")
    print("=" * 70)
    print(f"🌐 Agent Address: {invoice_chat_agent.address}")
    print(f"💰 Wallet Address: {invoice_chat_agent.wallet.address()}")
    print(f"🔄 Protocol: InvoiceChainChatProtocol v1.0.0")
    print(f"📡 Endpoint: http://127.0.0.1:8002/submit")
    print(f"🔑 GPT Available: {'✅ Yes' if GPT_AVAILABLE else '❌ No'}")
    print("=" * 70)
    print("💬 Ready for intelligent conversations via Agentverse!")
    print("🔗 Connect via: https://agentverse.ai")
    print("📋 Protocol manifest published for agent discovery")
    print("=" * 70)
    
    # Run the official uAgent with published manifest
    invoice_chat_agent.run()
