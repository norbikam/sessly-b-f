.PHONY: help install run test migrate shell clean deploy check lint

help:
	@echo "Sessly Backend - Available Commands"
	@echo "===================================="
	@echo ""
	@echo "Development:"
	@echo "  make install    - Install dependencies"
	@echo "  make run        - Start development server"
	@echo "  make shell      - Open Django shell"
	@echo "  make test       - Run all tests"
	@echo "  make migrate    - Apply database migrations"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean      - Remove cache files"
	@echo "  make check      - Check for issues"
	@echo "  make lint       - Run code linters"
	@echo ""
	@echo "Deployment:"
	@echo "  make deploy     - Deploy to production"
	@echo "  make static     - Collect static files"
	@echo ""

install:
	@echo "📦 Installing dependencies..."
	pip install --upgrade pip
	pip install -r requirements.txt
	@echo "✅ Done!"

run:
	@echo "🚀 Starting development server..."
	python3 manage.py runserver

migrate:
	@echo "🗃️  Creating and applying migrations..."
	python3 manage.py makemigrations
	python3 manage.py migrate
	@echo "✅ Migrations applied!"

shell:
	@echo "🐚 Opening Django shell..."
	python3 manage.py shell

test:
	@echo "🧪 Running tests..."
	python3 manage.py test --verbosity=2

test-users:
	@echo "🧪 Testing users app..."
	python3 manage.py test users --verbosity=2

test-businesses:
	@echo "🧪 Testing businesses app..."
	python3 manage.py test businesses --verbosity=2

clean:
	@echo "🧹 Cleaning cache files..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleaned!"

check:
	@echo "🔍 Checking for issues..."
	python3 manage.py check

check-deploy:
	@echo "🔍 Checking deployment configuration..."
	python3 manage.py check --deploy

static:
	@echo "📦 Collecting static files..."
	python3 manage.py collectstatic --noinput

deploy:
	@echo "🚀 Deploying to production..."
	vercel --prod

lint:
	@echo "🔍 Running linters..."
	@command -v flake8 >/dev/null 2>&1 && flake8 . || echo "⚠️  flake8 not installed"
	@command -v black >/dev/null 2>&1 && black --check . || echo "⚠️  black not installed"

format:
	@echo "✨ Formatting code..."
	@command -v black >/dev/null 2>&1 && black . || echo "⚠️  black not installed (pip install black)"

superuser:
	@echo "👤 Creating superuser..."
	python3 manage.py createsuperuser

seed:
	@echo "🌱 Seeding sample data..."
	python3 manage.py seed_sample_business

logs:
	@echo "📋 Viewing logs..."
	tail -f logs/app.log

showmigrations:
	@echo "📋 Showing migration status..."
	python3 manage.py showmigrations

flush:
	@echo "⚠️  Flushing database..."
	python3 manage.py flush

setup:
	@echo "🔧 Running setup script..."
	./setup.sh
