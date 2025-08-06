from openai import OpenAI
from dotenv import load_dotenv
import os
import traceback

# Load environment variables from the project root
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)

def get_openai_client():
    """Get OpenAI client instance with API key"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    
    try:
        client = OpenAI(
            api_key=api_key,
            base_url=os.getenv("OPENAI_API_BASE")  # Optional: for OpenRouter or other providers
        )
        return client
    except Exception as e:
        print(f"Failed to create OpenAI client: {e}")
        return None

def explain_validation(invoice_data, issues, validation_details=None):
    """Generate explanation for invoice validation result with enhanced context"""
    
    # Check if OpenAI API key is available
    client = get_openai_client()
    if not client:
        # Enhanced fallback explanation
        if not issues:
            score = validation_details.get('overall_score', 100) if validation_details else 100
            return f"✅ Invoice {invoice_data.get('invoice_id', 'Unknown')} APPROVED (Score: {score}/100) - All validation stages passed. Vendor: {invoice_data.get('vendor_name', 'Unknown')}, Amount: ${float(invoice_data.get('amount', 0)):.2f}. Ready for processing and blockchain logging."
        else:
            critical_issues = [i for i in issues if "CRITICAL" in i]
            if critical_issues:
                return f"🚨 Invoice {invoice_data.get('invoice_id', 'Unknown')} REJECTED - Critical issues detected: {'; '.join(critical_issues)}. Immediate review required."
            else:
                return f"⚠️ Invoice {invoice_data.get('invoice_id', 'Unknown')} REJECTED - Validation failed. Issues: {'; '.join(issues[:3])}{'...' if len(issues) > 3 else ''}. Please correct and resubmit."
    
    try:
        
        # Create detailed context for AI
        validation_summary = ""
        if validation_details:
            validation_summary = f"""
Validation Pipeline Results:
- Basic Validation: {'✅' if validation_details['basic_validation']['passed'] else '❌'} (Score: {validation_details['basic_validation']['score']}/25)
- ERP Cross-checks: {'✅' if validation_details['erp_validation']['passed'] else '❌'} (Score: {validation_details['erp_validation']['score']}/30)
- Contextual Logic: {'✅' if validation_details['contextual_validation']['passed'] else '❌'} (Score: {validation_details['contextual_validation']['score']}/25)
- Fraud Detection: {'✅' if validation_details['fraud_detection']['passed'] else '❌'} (Score: {validation_details['fraud_detection']['score']}/20)
- Overall Score: {validation_details['overall_score']}/100

ERP Details: {validation_details.get('erp_validation', {}).get('details', {})}
"""
        
        prompt = f"""
You are an expert AI finance compliance auditor for an enterprise ERP system. Analyze this invoice validation and provide a professional, actionable explanation.

Invoice Data:
{invoice_data}

{validation_summary}

Validation Issues Found:
{issues if issues else 'None - All checks passed'}

Please provide a response in this exact format:

Status: [APPROVED/APPROVED_WITH_CONDITIONS/REJECTED]
Summary: [2-3 sentence executive summary of the decision]
Key Issues: [Most critical 1-2 issues that need attention, or "None" if approved]
Business Impact: [Brief explanation of what this means for accounts payable]
Next Steps: [Specific actionable recommendations]
Confidence: [1-10 scale of decision confidence]

Keep the tone professional but accessible to finance teams. Focus on business impact and compliance requirements.
"""

        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",  # OpenRouter model name
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"OpenAI API Error: {e}")
        # Enhanced fallback explanation
        if not issues:
            score = validation_details.get('overall_score', 100) if validation_details else 100
            return f"✅ Invoice {invoice_data.get('invoice_id', 'Unknown')} APPROVED (Score: {score}/100) - All validation stages passed. Vendor: {invoice_data.get('vendor_name', 'Unknown')}, Amount: ${float(invoice_data.get('amount', 0)):.2f}. Ready for processing and blockchain logging."
        else:
            critical_issues = [i for i in issues if "CRITICAL" in i]
            if critical_issues:
                return f"🚨 Invoice {invoice_data.get('invoice_id', 'Unknown')} REJECTED - Critical issues detected: {'; '.join(critical_issues)}. Immediate review required."
            else:
                return f"⚠️ Invoice {invoice_data.get('invoice_id', 'Unknown')} REJECTED - Validation failed. Issues: {'; '.join(issues[:3])}{'...' if len(issues) > 3 else ''}. Please correct and resubmit."
