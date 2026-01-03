#!/bin/bash
# Sessly Backend Setup Script

echo "🚀 Sessly Backend Setup"
echo "======================"
echo ""

# Check Python version
echo "📌 Checking Python version..."
python3 --version || { echo "❌ Python 3 not found"; exit 1; }

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found"
    echo "📝 Creating .env from template..."
    cp .env.example .env
    echo "✅ .env file created - PLEASE EDIT IT WITH YOUR SETTINGS"
else
    echo "✅ .env file exists"
fi

# Run migrations
echo "🗃️  Running migrations..."
python3 manage.py migrate

# Check deployment readiness
echo "🔍 Checking deployment configuration..."
python3 manage.py check --deploy

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Create superuser: python3 manage.py createsuperuser"
echo "3. Run development server: python3 manage.py runserver"
echo ""
echo "📚 Documentation:"
echo "- Quick Deploy: docs/QUICK_DEPLOY.md"
echo "- Implementation Plan: docs/IMPLEMENTATION_PLAN.md"
echo "- Error Codes: docs/ERROR_CODES.md"
