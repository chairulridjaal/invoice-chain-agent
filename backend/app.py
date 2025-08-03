#!/usr/bin/env python3
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.invoice_agent import app, invoice_agent
from threading import Thread
import time

def start_agent():
    """Start the uAgent in a separate thread"""
    print("Starting uAgent...")
    invoice_agent.run()

if __name__ == "__main__":
    # Start uAgent in background thread
    agent_thread = Thread(target=start_agent, daemon=True)
    agent_thread.start()
    
    # Give the agent a moment to start
    time.sleep(2)
    
    # Run Flask app (this will be managed by gunicorn in production)
    port = int(os.getenv("PORT", "8001"))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"Starting Flask server on {host}:{port}")
    app.run(host=host, port=port, debug=False)
