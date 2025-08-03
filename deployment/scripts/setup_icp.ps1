# PowerShell setup script for Windows
Write-Host "🚀 Setting up Invoice Chain Agent with ICP Integration" -ForegroundColor Green

# Check if dfx is installed
try {
    $dfxVersion = dfx --version
    Write-Host "✅ dfx CLI found: $dfxVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ dfx CLI not found. Please install it first:" -ForegroundColor Red
    Write-Host "sh -ci `"$(curl -fsSL https://internetcomputer.org/install.sh)`"" -ForegroundColor Yellow
    exit 1
}

# Navigate to canister directory
Set-Location canister

# Start local dfx
Write-Host "🔧 Starting local dfx replica..." -ForegroundColor Blue
dfx start --background --clean

# Deploy the canister
Write-Host "📦 Deploying invoice_logger canister..." -ForegroundColor Blue
dfx deploy invoice_logger

# Get canister ID
$CANISTER_ID = dfx canister id invoice_logger
Write-Host "✅ Canister deployed with ID: $CANISTER_ID" -ForegroundColor Green

# Test canister health
Write-Host "🩺 Testing canister health..." -ForegroundColor Blue
dfx canister call invoice_logger health

# Create .env file with canister ID
Set-Location ..
@"
CANISTER_ID=$CANISTER_ID
ICP_NETWORK=local
DFX_PATH=dfx
"@ | Out-File -FilePath ".env" -Encoding UTF8

Write-Host ""
Write-Host "🎉 Setup complete!" -ForegroundColor Green
Write-Host "📝 Canister ID saved to .env file" -ForegroundColor Green
Write-Host "🌐 Your invoice logger canister is running at: $CANISTER_ID" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Add your OpenAI API key to .env: OPENAI_API_KEY=your_key_here"
Write-Host "2. Run: python agents/invoice_agent.py"
Write-Host "3. Test with: python test_send.py"
Write-Host ""
Write-Host "For production deployment:" -ForegroundColor Cyan
Write-Host "1. Deploy canister to IC testnet: dfx deploy --network testnet"
Write-Host "2. Update .env with testnet canister ID"
Write-Host "3. Deploy to Render with environment variables"
