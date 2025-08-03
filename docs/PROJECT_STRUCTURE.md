# Invoice Chain Agent - Project Structure

## 📁 Directory Structure

```
invoice-chain-agent/
├── backend/                    # Python Backend
│   ├── app.py                 # Main Flask application entry point
│   ├── wsgi.py                # WSGI entry point for production
│   ├── requirements.txt       # Python dependencies
│   ├── agents/                # uAgents Multi-Agent System
│   │   ├── invoice_agent.py   # Main invoice validation agent
│   │   ├── audit_agent.py     # Audit and compliance agent
│   │   └── vendor_agent.py    # Vendor verification agent
│   ├── blockchain/            # ICP Blockchain Integration
│   │   ├── __init__.py
│   │   └── integration.py     # Blockchain logging and smart contracts
│   └── utils/                 # Utility Modules
│       ├── __init__.py
│       ├── invoice_validator.py  # Business logic validation
│       ├── ocr_processor.py      # OCR + GPT-4 document processing
│       └── openai_explain.py    # AI-powered explanations
├── frontend/                   # React Frontend
│   ├── package.json
│   ├── vite.config.js
│   ├── src/
│   │   ├── App.jsx            # Main React component
│   │   ├── DocumentUpload.jsx # File upload interface
│   │   └── main.jsx
│   └── dist/                  # Built frontend assets
├── canister/                   # ICP Smart Contract
│   ├── dfx.json               # DFX configuration
│   └── src/
│       └── invoice_logger.mo  # Motoko smart contract
├── deployment/                 # Deployment Configuration
│   ├── render.yaml            # Render.com deployment config
│   ├── Procfile               # Process configuration
│   └── scripts/               # Deployment scripts
│       ├── deploy_prep.bat    # Windows deployment prep
│       ├── deploy_prep.ps1    # PowerShell deployment prep
│       ├── build.sh           # Linux build script
│       ├── setup_icp.ps1      # ICP setup for Windows
│       └── setup_icp.sh       # ICP setup for Linux
├── docs/                       # Documentation
│   └── DEPLOYMENT.md          # Deployment instructions
├── tests/                      # Test Files
│   └── test_send.py           # Integration tests
├── data/                       # Sample Data
│   └── erp_mock.json          # Mock ERP data
├── static/                     # Static Assets (built frontend)
├── requirements.txt            # Root Python dependencies
├── runtime.txt                 # Python version specification
├── .env.example               # Environment variables template
└── README.md                  # Main project documentation
```

## 🏗️ Architecture Overview

### Backend Architecture

- **Flask Web Server**: REST API endpoints for invoice processing
- **uAgents Framework**: Multi-agent system for enterprise validation
- **ICP Integration**: Blockchain logging via HTTP API
- **OCR + AI**: Tesseract OCR with GPT-4 intelligent extraction

### Frontend Architecture

- **React + Vite**: Modern frontend with fast development
- **Real-time Updates**: Live validation status and progress
- **File Upload**: Drag-and-drop document processing

### Blockchain Architecture

- **ICP Canister**: Motoko smart contract for immutable storage
- **HTTP API**: Production-ready blockchain integration
- **Audit Trail**: Complete validation history on-chain

## 🚀 Quick Start

1. **Backend Setup**:

   ```bash
   cd backend
   pip install -r requirements.txt
   python app.py
   ```

2. **Frontend Setup**:

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Deployment**:
   ```bash
   cd deployment/scripts
   ./deploy_prep.bat  # Windows
   ```

## 🔧 Environment Variables

```bash
# Required
OPENAI_API_KEY=your_openrouter_api_key

# Optional
CANISTER_ID=uxrrr-q7777-77774-qaaaq-cai
ICP_NETWORK=testnet
HOST=0.0.0.0
PORT=8001
```

## 📋 Development Workflow

1. **Backend Development**: Work in `/backend` directory
2. **Frontend Development**: Work in `/frontend` directory
3. **Blockchain Development**: Work in `/canister` directory
4. **Deployment**: Use scripts in `/deployment/scripts`
5. **Documentation**: Update files in `/docs` directory

This structure provides clear separation of concerns and makes the project much easier to navigate and maintain.
