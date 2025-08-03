#!/usr/bin/env python3
"""
Vercel serverless function entry point
"""
import os
import sys

# Add the backend directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_dir = os.path.join(project_root, 'backend')
sys.path.insert(0, backend_dir)
sys.path.insert(0, project_root)

# Set environment variables
os.environ.setdefault('CANISTER_ID', 'uxrrr-q7777-77774-qaaaq-cai')
os.environ.setdefault('ICP_NETWORK', 'testnet')
os.environ.setdefault('OPENAI_API_BASE', 'https://openrouter.ai/api/v1')

# Import the Flask app from backend
try:
    from backend.agents.invoice_agent import app
except ImportError:
    # Fallback import
    sys.path.insert(0, os.path.join(backend_dir, 'agents'))
    from invoice_agent import app

# Vercel expects the app to be available as a module-level variable
application = app

# For Vercel serverless functions
def handler(event, context):
    return app

if __name__ == "__main__":
    # For local development
    app.run(debug=True, host='0.0.0.0', port=8000)
