# 🧾 Invoice Chain Agent

An intelligent multi-agent system for invoice validation and blockchain logging using **Fetch.ai uAgents** and **Internet Computer Protocol (ICP)** canisters.

## � Project Structure

This project is organized into clear, focused directories:

- **`backend/`** - Python Flask API + uAgents system
- **`frontend/`** - React web interface
- **`canister/`** - ICP smart contract (Motoko)
- **`deployment/`** - Deployment configs and scripts
- **`docs/`** - Documentation and guides
- **`tests/`** - Test files

📖 **[View Detailed Project Structure](docs/PROJECT_STRUCTURE.md)**

## �🚀 Features

- **🤖 Multi-Agent System**: Vendor, Invoice Processor, and Audit agents
- **🧠 AI-Powered Validation**: OpenAI GPT-4 explains validation results
- **⛓️ ICP Blockchain Integration**: Immutable logging on Internet Computer
- **🌐 REST API**: HTTP endpoints for web integration
- **📊 Real-time Monitoring**: Audit agent for continuous monitoring
- **☁️ Production Ready**: Configured for Render deployment

## 🏗️ Architecture

```
┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Vendor      │───▶│ Invoice Chain   │───▶│ ICP Canister    │
│ Agent       │    │ Agent           │    │ (Blockchain)    │
└─────────────┘    └─────────────────┘    └─────────────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │ Audit Agent     │
                   │ (Monitor)       │
                   └─────────────────┘
```

## 🛠️ Setup & Installation

### Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **dfx CLI** (for ICP development)

### 1. Install dfx CLI

```bash
sh -ci "$(curl -fsSL https://internetcomputer.org/install.sh)"
```

### 2. Clone and Setup

```bash
git clone <your-repo>
cd invoice-chain-agent
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r backend/requirements.txt
```

### 3. ICP Canister Setup

**Windows (PowerShell):**

```powershell
.\deployment\scripts\setup_icp.ps1
```

**macOS/Linux:**

```bash
chmod +x deployment/scripts/setup_icp.sh
./deployment/scripts/setup_icp.sh
```

### 4. Environment Configuration

Copy `.env.example` to `.env` and configure:

```env
OPENAI_API_KEY=your_openai_api_key_here
CANISTER_ID=your_canister_id_here
ICP_NETWORK=local
DFX_PATH=dfx
```

## 🚀 Running the System

### Local Development

1. **Start the Invoice Agent:**

```bash
cd backend
python agents/invoice_agent.py
```

2. **Test with Vendor Agent:**

```bash
cd backend
python agents/vendor_agent.py
```

3. **Monitor with Audit Agent:**

```bash
cd backend
python agents/audit_agent.py
```

### Testing Individual Components

```bash
# Test single invoice
python tests/test_send.py

# Test HTTP endpoint
curl -X POST http://localhost:8001/submit \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_id": "TEST-001",
    "vendor_name": "Test Corp",
    "tax_id": "123456789",
    "amount": 1000.00,
    "date": "2025-08-03"
  }'
```

## 🌐 API Endpoints

| Endpoint        | Method | Description                   |
| --------------- | ------ | ----------------------------- |
| `/submit`       | POST   | Submit invoice for validation |
| `/invoice/<id>` | GET    | Get invoice from blockchain   |
| `/audit/<id>`   | GET    | Get audit logs for invoice    |
| `/stats`        | GET    | Get system statistics         |
| `/health`       | GET    | Health check                  |

## ☁️ Production Deployment

### Render Deployment

1. **Deploy ICP Canister to Testnet:**

```bash
cd canister
dfx deploy --network testnet
```

2. **Configure Environment Variables in Render:**

```env
OPENAI_API_KEY=your_key
CANISTER_ID=your_testnet_canister_id
ICP_NETWORK=testnet
PORT=10000
```

3. **Deploy to Render:**

- Build Command: `cd backend && pip install -r requirements.txt`
- Start Command: `cd backend && gunicorn wsgi:application --bind 0.0.0.0:$PORT`

### Environment Variables

| Variable         | Description                     | Example           |
| ---------------- | ------------------------------- | ----------------- |
| `OPENAI_API_KEY` | OpenAI API key for explanations | `sk-...`          |
| `CANISTER_ID`    | ICP Canister ID                 | `rdmx6-jaaaa-...` |
| `ICP_NETWORK`    | ICP network (local/testnet/ic)  | `testnet`         |
| `PORT`           | Server port                     | `10000`           |
| `DFX_PATH`       | Path to dfx binary              | `dfx`             |

## 🧪 Testing

```bash
# Run all agents in separate terminals
cd backend && python agents/invoice_agent.py    # Terminal 1
cd backend && python agents/vendor_agent.py     # Terminal 2
cd backend && python agents/audit_agent.py      # Terminal 3

# Check ICP canister directly
cd canister
dfx canister call invoice_logger getStats
dfx canister call invoice_logger health
```

## 📊 Monitoring

The audit agent provides:

- Real-time invoice statistics
- System health monitoring
- Audit log tracking
- Blockchain connectivity status

## 🔧 Development

### Project Structure

```
invoice-chain-agent/
├── backend/               # Python Flask API + uAgents
│   ├── app.py            # Main Flask application
│   ├── wsgi.py           # Production entry point
│   ├── agents/           # uAgent implementations
│   │   ├── invoice_agent.py # Main processor
│   │   ├── vendor_agent.py  # Invoice sender
│   │   └── audit_agent.py   # Monitor
│   ├── blockchain/       # ICP integration
│   │   └── integration.py
│   ├── utils/            # Utilities
│   │   └── openai_explain.py
│   └── requirements.txt  # Python dependencies
├── frontend/             # React web interface
├── canister/             # ICP Canister (Motoko)
│   ├── src/
│   │   └── invoice_logger.mo
│   └── dfx.json
├── deployment/           # Deployment configs
│   ├── Procfile
│   ├── render.yaml
│   └── scripts/
├── docs/                 # Documentation
├── tests/                # Test files
└── data/                 # Sample data
```

### Adding New Features

1. **New Agent**: Create in `backend/agents/` directory
2. **New Endpoint**: Add to Flask app in `backend/agents/invoice_agent.py`
3. **Canister Updates**: Modify `canister/src/invoice_logger.mo`

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Test with local ICP canister
4. Submit pull request

## 📝 License

MIT License - see LICENSE file

---

**🎯 Next Steps:**

1. Deploy to IC testnet: `dfx deploy --network testnet`
2. Build frontend with Next.js/React
3. Add signature verification
4. Implement Merkle tree for audit trails
