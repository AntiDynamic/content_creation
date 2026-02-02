# Quick Setup Script for Windows
# YouTube Analysis Backend

Write-Host "🚀 YouTube Analysis Backend - Quick Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "1️⃣ Checking Python version..." -ForegroundColor Yellow
python --version

# Create virtual environment
Write-Host ""
Write-Host "2️⃣ Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate virtual environment
Write-Host ""
Write-Host "3️⃣ Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host ""
Write-Host "4️⃣ Installing dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip
pip install -r requirements.txt

# Copy environment file
Write-Host ""
Write-Host "5️⃣ Setting up environment file..." -ForegroundColor Yellow
if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
    Write-Host "✅ Created .env file - Please edit it with your API keys!" -ForegroundColor Green
} else {
    Write-Host "⚠️  .env file already exists, skipping..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit .env file with your API keys"
Write-Host "2. Start PostgreSQL and Redis"
Write-Host "3. Run: python main.py"
Write-Host ""
Write-Host "📚 See README.md for detailed instructions" -ForegroundColor Cyan
