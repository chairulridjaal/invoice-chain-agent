@echo off
echo 🚀 Preparing Invoice Chain Agent for Render Deployment...

echo 📦 Testing Python dependencies...
python -c "import pytesseract; print('✅ OCR dependencies working')"
python -c "import uagents; print('✅ uAgents working')"
python -c "import openai; print('✅ OpenAI client working')"

echo 🎨 Building React frontend...
cd frontend
call npm install
call npm run build
cd ..

echo 📁 Copying frontend build to static directory...
if exist static rmdir /s /q static
mkdir static
xcopy frontend\dist static /e /y

echo ✅ Deployment preparation complete!
echo 📋 Next steps:
echo   1. Commit and push to GitHub
echo   2. Connect repository to Render
echo   3. Set environment variables in Render dashboard
echo   4. Deploy!
