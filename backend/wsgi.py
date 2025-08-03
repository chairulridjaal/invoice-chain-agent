#!/usr/bin/env python3
"""
WSGI entry point for cloud deployment
(DigitalOcean, Google Cloud Run, AWS, Azure, etc.)
"""
import os
import sys
from threading import Thread

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.invoice_agent import app, invoice_agent

def create_app():
    """Create and configure the Flask app for WSGI"""
    # Set production environment variables
    os.environ.setdefault('HOST', '0.0.0.0')
    os.environ.setdefault('PORT', str(os.getenv('PORT', '10000')))
    os.environ.setdefault('AGENT_PORT', '8000')
    os.environ.setdefault('ICP_NETWORK', 'testnet')  # Use testnet for production
    
    # Build frontend if in production
    if os.getenv('NODE_ENV') == 'production':
        build_frontend()
    
    # Start the uAgent in a separate thread for WSGI deployment
    def start_agent():
        try:
            print("Starting uAgent in background thread...")
            invoice_agent.run()
        except Exception as e:
            print(f"Error starting agent: {e}")
    
    # Only start agent thread if we're in the main process (not in gunicorn worker)
    if os.getenv('GUNICORN_CMD_ARGS') is None:
        agent_thread = Thread(target=start_agent, daemon=True)
        agent_thread.start()
    
    return app

def build_frontend():
    """Build frontend for production"""
    try:
        import subprocess
        print("Building frontend for production...")
        subprocess.run(['npm', 'install'], cwd='frontend', check=True)
        subprocess.run(['npm', 'run', 'build'], cwd='frontend', check=True)
        
        # Copy built files to static directory
        import shutil
        if os.path.exists('static'):
            shutil.rmtree('static')
        shutil.copytree('frontend/dist', 'static')
        print("Frontend built successfully!")
    except Exception as e:
        print(f"Error building frontend: {e}")

# For Render deployment
application = create_app()

if __name__ == "__main__":
    port = int(os.getenv('PORT', '10000'))
    application.run(host='0.0.0.0', port=port, debug=False)
