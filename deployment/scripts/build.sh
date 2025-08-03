#!/bin/bash

echo "🚀 Building Invoice Chain Agent for Production..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Build frontend
echo "🎨 Building frontend..."
cd frontend
npm install
npm run build
cd ..

# Create static file serving
echo "📁 Setting up static file serving..."
mkdir -p static
cp -r frontend/dist/* static/

echo "✅ Build complete!"
echo "Frontend built and ready for static serving"
echo "Backend ready for WSGI deployment"
