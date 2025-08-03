from openai import OpenAI
from dotenv import load_dotenv
import os
import traceback

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE")
)

def explain_validation(invoice_data, issues):
    prompt = f"""
You are an AI compliance auditor. Analyze the following invoice and validation results, and respond in this format:

Explanation: <brief, professional explanation of the status in 2–3 sentences, including key compliance issues>
Suggestion: <what the sender should do to correct the invoice>
Confidence: <1–10, how confident you are in your explanation>

Invoice:
{invoice_data}

Validation Issues:
{issues if issues else 'None'}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        traceback.print_exc()
        return f"Error generating explanation: {e}"
