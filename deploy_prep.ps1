# Production Deployment Preparation Script
Write-Host "🚀 Preparing Invoice Chain Agent for Render Deployment..." -ForegroundColor Green

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Test dependencies
Write-Host "📦 Testing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Build frontend
Write-Host "🎨 Building React frontend..." -ForegroundColor Yellow
cd frontend
npm install
npm run build
cd ..

# Copy frontend build
Write-Host "📁 Copying frontend build to static directory..." -ForegroundColor Yellow
if (Test-Path "static") { Remove-Item "static" -Recurse -Force }
mkdir static
Copy-Item "frontend/dist/*" "static/" -Recurse

# Test OCR functionality
Write-Host "🔍 Testing OCR functionality..." -ForegroundColor Yellow
python -c "import pytesseract; import PIL; print('✅ OCR dependencies working')"

# Test uAgents
Write-Host "🤖 Testing uAgents..." -ForegroundColor Yellow
python -c "import uagents; print('✅ uAgents working')"

# Test OpenAI integration
Write-Host "🧠 Testing OpenAI integration..." -ForegroundColor Yellow
python -c "import openai; print('✅ OpenAI client working')"

Write-Host "✅ Deployment preparation complete!" -ForegroundColor Green
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "  1. Commit and push to GitHub" -ForegroundColor White
Write-Host "  2. Connect repository to Render" -ForegroundColor White
Write-Host "  3. Set environment variables in Render dashboard" -ForegroundColor White
Write-Host "  4. Deploy!" -ForegroundColor White
