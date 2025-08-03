# 🚀 Quick Start Guide for Invoice Chain Agent

## You're All Set! Here's how to get started:

### 🔧 Environment Setup (COMPLETED ✅)

- ✅ Python environment configured
- ✅ Backend dependencies installed
- ✅ Frontend dependencies installed
- ✅ Environment file created (`.env`)

### 🎯 Next Steps:

#### 1. Configure Your API Keys

Edit the `.env` file in the root directory and add your OpenAI API key:

```bash
OPENAI_API_KEY=your_actual_openai_api_key_here
```

#### 2. Start the Development Environment

**Option A: Using VS Code Tasks (Recommended)**

- Press `Ctrl+Shift+P` and search "Tasks: Run Task"
- Select "Start Backend (Invoice Agent)"
- Then start the frontend manually: `cd frontend && npm run dev`

**Option B: Manual Terminal Commands**

```powershell
# Terminal 1 - Backend
cd backend
C:/Users/User/AppData/Local/Microsoft/WindowsApps/python3.11.exe app.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

#### 3. Test the System

- Backend will run on: http://localhost:8001
- Frontend will run on: http://localhost:5173 (Vite default)
- API Health Check: http://localhost:8001/health

#### 4. Key Features to Explore:

**🤖 Multi-Agent System:**

- `vendor_agent.py` - Simulates invoice submissions
- `invoice_agent.py` - Main validation engine with AI
- `audit_agent.py` - Monitoring and compliance

**🧠 AI-Powered Validation:**

- Uses OpenAI GPT-4 for intelligent explanations
- Multi-layered validation pipeline
- Fraud detection algorithms

**⛓️ Blockchain Integration:**

- ICP (Internet Computer) canister logging
- Immutable audit trails
- Smart contract validation

**🌐 REST API Endpoints:**

- `POST /submit` - Submit invoice for validation
- `GET /health` - System health check
- `GET /stats` - System statistics
- `GET /invoice/<id>` - Retrieve invoice from blockchain

### 🧪 Testing the System

1. **Test API Health:**

```bash
curl http://localhost:8001/health
```

2. **Submit Test Invoice:**

```bash
curl -X POST http://localhost:8001/submit -H "Content-Type: application/json" -d '{
  "invoice_id": "TEST-001",
  "vendor_name": "Test Corp",
  "tax_id": "123456789",
  "amount": 1000.00,
  "date": "2025-08-03"
}'
```

3. **Use the Web Interface:**

- Open http://localhost:5173 in your browser
- Upload invoice documents or fill in manual data
- Watch real-time validation results

### 🔍 Project Architecture Overview:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Web     │───▶│ Flask API +     │───▶│ ICP Blockchain  │
│   Interface     │    │ uAgents System  │    │ Canister        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ OpenAI GPT-4    │
                       │ Explanations    │
                       └─────────────────┘
```

### 📁 Key Files to Understand:

- **`backend/agents/invoice_agent.py`** - Main agent with validation logic
- **`backend/utils/invoice_validator.py`** - Validation rules engine
- **`backend/utils/openai_explain.py`** - AI explanation generation
- **`backend/blockchain/integration.py`** - ICP blockchain interface
- **`frontend/src/App.jsx`** - Main React application
- **`frontend/src/DocumentUpload.jsx`** - OCR document processing

### 🎉 You're Ready to Code!

The project is now fully set up and ready for development. Start by running the backend and frontend, then explore the codebase to understand the multi-agent architecture.

For blockchain features, you'll need to set up the ICP canister separately (see README.md for details).
