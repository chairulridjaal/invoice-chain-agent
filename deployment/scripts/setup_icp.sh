#!/bin/bash

echo "🚀 Setting up Invoice Chain Agent with ICP Integration"

# Check if dfx is installed
if ! command -v dfx &> /dev/null; then
    echo "❌ dfx CLI not found. Please install it first:"
    echo "sh -ci \"$(curl -fsSL https://internetcomputer.org/install.sh)\""
    exit 1
fi

echo "✅ dfx CLI found"

# Navigate to canister directory
cd canister

# Start local dfx
echo "🔧 Starting local dfx replica..."
dfx start --background --clean

# Deploy the canister
echo "📦 Deploying invoice_logger canister..."
dfx deploy invoice_logger

# Get canister ID
CANISTER_ID=$(dfx canister id invoice_logger)
echo "✅ Canister deployed with ID: $CANISTER_ID"

# Test canister health
echo "🩺 Testing canister health..."
dfx canister call invoice_logger health

# Create .env file with canister ID
cd ..
echo "CANISTER_ID=$CANISTER_ID" > .env
echo "ICP_NETWORK=local" >> .env
echo "DFX_PATH=dfx" >> .env

echo ""
echo "🎉 Setup complete!"
echo "📝 Canister ID saved to .env file"
echo "🌐 Your invoice logger canister is running at: $CANISTER_ID"
echo ""
echo "Next steps:"
echo "1. Add your OpenAI API key to .env: OPENAI_API_KEY=your_key_here"
echo "2. Run: python agents/invoice_agent.py"
echo "3. Test with: python test_send.py"
echo ""
echo "For production deployment:"
echo "1. Deploy canister to IC testnet: dfx deploy --network testnet"
echo "2. Update .env with testnet canister ID"
echo "3. Deploy to Render with environment variables"
