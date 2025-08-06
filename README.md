# 🧾 Invoice Chain Agent

**NextGen AI Agent for Invoice Validation & Blockchain Storage**  
_Built for Fetch.ai & Internet Computer Hackathon 2025_

A comprehensive invoice processing system that combines AI-powered validation, fraud detection, and blockchain storage using Fetch.ai uAgents and Internet Computer Protocol (ICP).

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-ICP%20%7C%20Fetch.ai-green.svg)
![Status](https://img.shields.io/badge/status-Active%20Development-orange.svg)

## 🚀 **Features**

### **🤖 AI-Powered Processing**

- **GPT Integration**: Intelligent invoice analysis with OpenRouter/OpenAI
- **Multi-Layer Validation**: Basic, ERP cross-checks, contextual logic, fraud detection
- **OCR Processing**: Extract data from invoice images and PDFs
- **Risk Assessment**: Advanced fraud detection with confidence scoring

### **⛓️ Blockchain Integration**

- **ICP Canister Storage**: Immutable invoice records on Internet Computer
- **Privacy-First**: Only metadata stored on-chain, sensitive data encrypted
- **Real-time Verification**: Live blockchain confirmation with transaction hashes
- **Audit Trail**: Complete processing history with timestamps

### **🎯 Fetch.ai uAgent Protocol**

- **Chat Interface**: Natural language queries about invoice status
- **Agent Discovery**: Registered in Fetch.ai Agentverse with published manifest
- **Inter-Agent Communication**: Standard uAgent Protocol message handling
- **Privacy Protection**: GPT responses only include non-sensitive metadata

### **💻 Modern Web Interface**

- **React Frontend**: Responsive UI with real-time processing stages
- **File Upload**: Support for PDF, PNG, JPG invoice documents
- **Manual Entry**: Form-based invoice submission with validation
- **Live Dashboard**: Processing status, validation results, blockchain confirmation

## 🏗️ **Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │   Flask Backend │    │  ICP Canister   │
│   (Port 3000)   │◄──►│   (Port 8001)   │◄──►│  Blockchain DB  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                       ┌─────────────────┐
                       │ Fetch.ai uAgent │
                       │   (Port 8000)   │
                       │  Chat Protocol  │
                       └─────────────────┘
```

## 🛠️ **Tech Stack**

### **Frontend**

- **React 18** with TypeScript
- **Vite** for fast development and builds
- **Tailwind CSS** for styling
- **Lucide React** for icons
- **React Router** for navigation

### **Backend**

- **Python 3.11+** with Flask
- **Fetch.ai uAgents** for agent protocol
- **OpenAI/OpenRouter** for GPT integration
- **Subprocess** for ICP dfx commands
- **CORS** enabled for cross-origin requests

### **Blockchain**

- **Internet Computer Protocol (ICP)**
- **Motoko** smart contract language
- **DFX SDK** for canister management
- **Local/Testnet/Mainnet** deployment support

### **AI & ML**

- **GPT-3.5-turbo** via OpenRouter
- **Custom validation logic** with scoring algorithms
- **Fraud detection models** with risk assessment
- **OCR processing** for document extraction

## 📋 **Prerequisites**

- **Node.js 18+** and npm
- **Python 3.11+** with pip
- **DFX SDK** for ICP development
- **WSL2** (Windows) or **native shell** (macOS/Linux)
- **OpenRouter API key** for GPT integration

## 🔧 **Development**

### **Project Structure**

```
invoice-chain-agent/
├── frontend/           # React application
├── backend/            # Flask API + uAgent
├── canister/           # ICP Motoko smart contract
├── blockchain/         # Blockchain integration utilities
├── docs/              # Documentation
├── .env               # Environment variables
└── README.md          # This file
```

### **Environment Variables**

```bash
# Required for GPT integration
OPENAI_API_KEY=your_api_key
OPENAI_API_BASE=https://openrouter.ai/api/v1

# ICP Configuration
CANISTER_ID=your_canister_id
ICP_NETWORK=local
DFX_PATH=dfx

# Server Configuration
PORT=8001
HOST=0.0.0.0
```

## 🧪 **Testing**

### **API Endpoints**

- **Health Check:** `GET http://localhost:8001/health`
- **Submit Invoice:** `POST http://localhost:8001/submit`
- **Upload File:** `POST http://localhost:8001/upload`
- **Get Invoices:** `GET http://localhost:8001/invoices`
- **Chat Agent:** `POST http://localhost:8001/chat`

### **Canister Methods**

```bash
# Store invoice
dfx canister call invoice_storage storeInvoice '("INV-001", "Vendor", "TAX123", 1000.0, "2025-08-06", "approved", "notes", null, 85, 15, "LOW")'

# Get all invoices
dfx canister call invoice_storage getAllInvoices '()'

# Get specific invoice
dfx canister call invoice_storage getInvoice '("INV-001")'
```

## 🌐 **Deployment**

### **Frontend (Vercel/Netlify)**

```bash
cd frontend
npm run build
# Deploy dist/ folder
```

### **Backend (Railway/Heroku)**

```bash
# Procfile included for platform deployment
web: gunicorn --bind 0.0.0.0:$PORT backend.app:app
```

### **ICP Mainnet**

```bash
dfx deploy --network=ic --with-cycles=1000000000000
```

## 🤝 **Fetch.ai uAgent Integration**

### **Chat Protocol**

The system implements official Fetch.ai uAgent Chat Protocol:

```python
# Message Models
class InvoiceQueryMessage(Model):
    text: str
    query_type: str = "general"
    invoice_id: Optional[str] = None

class InvoiceResponseMessage(Model):
    text: str
    success: bool = True
    metadata: Optional[Dict] = None
```

### **Agent Discovery**

- **Published Manifest:** Registered in Fetch.ai Almanac
- **Agentverse Ready:** Discoverable by other agents
- **Standard Protocol:** Inter-agent communication support

## 🔒 **Privacy & Security**

- **🔐 Encrypted Storage:** Sensitive data encrypted before blockchain storage
- **🎭 Metadata Only:** GPT integration only receives non-sensitive metadata
- **🛡️ Fraud Detection:** Advanced risk scoring with confidence levels
- **📝 Audit Logs:** Complete processing history with timestamps
- **🔑 API Security:** Environment-based configuration management

## 📊 **Validation Pipeline**

1. **Basic Validation (25 pts):** Format, required fields, data types
2. **ERP Cross-checks (30 pts):** Vendor verification, duplicate detection
3. **Contextual Logic (25 pts):** Business rules, amount validation
4. **Fraud Detection (20 pts):** Risk patterns, anomaly detection

**Total Score:** 100 points → **Status:** Approved/Conditional/Rejected

## 🛣️ **Roadmap**

- [ ] **Mainnet Deployment:** ICP production canister
- [ ] **Multi-Agent System:** Specialized validation agents
- [ ] **Enterprise Features:** Batch processing, API webhooks
- [ ] **Mobile App:** React Native companion
- [ ] **Advanced Analytics:** Dashboard with insights

## 🤝 **Contributing**

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ for the future of AI-powered business automation**
