#!/bin/bash
# Quick setup script for YouTube Analysis Backend

echo "🚀 YouTube Analysis Backend - Quick Setup"
echo "=========================================="
echo ""

# Check Python version
echo "1️⃣ Checking Python version..."
python --version

# Create virtual environment
echo ""
echo "2️⃣ Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo ""
echo "3️⃣ Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install dependencies
echo ""
echo "4️⃣ Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Copy environment file
echo ""
echo "5️⃣ Setting up environment file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env file - Please edit it with your API keys!"
else
    echo "⚠️  .env file already exists, skipping..."
fi

echo ""
echo "=========================================="
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Start PostgreSQL and Redis"
echo "3. Run: python main.py"
echo ""
echo "📚 See README.md for detailed instructions"
