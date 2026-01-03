# 🔧 Sessly - Useful Commands

## Development

### Start Development Server
```bash
python3 manage.py runserver
# API available at http://localhost:8000/api/
```

### Create Superuser
```bash
python3 manage.py createsuperuser
# Access admin panel at http://localhost:8000/admin/
```

### Run Tests
```bash
# All tests
python3 manage.py test

# Specific app
python3 manage.py test users
python3 manage.py test businesses

# With verbosity
python3 manage.py test --verbosity=2

# Keep test database for faster subsequent runs
python3 manage.py test --keepdb
```

### Database Management
```bash
# Create migrations
python3 manage.py makemigrations

# Apply migrations
python3 manage.py migrate

# Show migration status
python3 manage.py showmigrations

# Rollback migration
python3 manage.py migrate users 0001

# SQL for migration (without running)
python3 manage.py sqlmigrate users 0001
```

### Seed Data
```bash
# Create sample business with data
python3 manage.py seed_sample_business
```

### Django Shell
```bash
# Interactive Python shell with Django
python3 manage.py shell

# Example commands in shell:
from users.models import User
from businesses.models import Business, Appointment

# List all users
User.objects.all()

# Get business by slug
Business.objects.get(slug='my-salon')

# Count pending appointments
Appointment.objects.filter(status='pending').count()
```

## Deployment

### Check Configuration
```bash
# Check for issues
python3 manage.py check

# Check deployment readiness (production warnings)
python3 manage.py check --deploy
```

### Static Files
```bash
# Collect static files for production
python3 manage.py collectstatic --noinput
```

### Generate Secret Key
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Vercel Deployment
```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy to preview
vercel

# Deploy to production
vercel --prod
```

## Debugging

### View Logs
```bash
# Django logs (development)
tail -f logs/django.log

# Application logs
tail -f logs/app.log

# Error logs only
grep ERROR logs/app.log
```

### Test Email
```bash
# In Django shell
python3 manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail(
...     'Test Subject',
...     'Test Message',
...     'from@example.com',
...     ['to@example.com'],
... )
```

### Database Connection Test
```bash
python3 manage.py dbshell
```

## Maintenance

### Clear Cache
```bash
python3 manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()
```

### Delete All Sessions
```bash
python3 manage.py clearsessions
```

### Flush Database (CAREFUL!)
```bash
# Delete all data
python3 manage.py flush

# Delete database and recreate
python3 manage.py flush --noinput
python3 manage.py migrate
```

## Docker (Optional)

### Build Image
```bash
docker build -t sessly-backend .
```

### Run Container
```bash
docker run -p 8000:8000 \
  -e DATABASE_URL="your-db-url" \
  -e DJANGO_SECRET_KEY="your-secret" \
  sessly-backend
```

## Testing API

### Using curl
```bash
# Register user
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "first_name": "Test",
    "last_name": "User"
  }'

# Login
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }'

# Use token
curl http://localhost:8000/api/businesses/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Using HTTPie (Better than curl)
```bash
# Install
pip install httpie

# Register
http POST localhost:8000/api/users/register/ \
  email=test@example.com \
  password=TestPassword123! \
  first_name=Test \
  last_name=User

# Login
http POST localhost:8000/api/users/login/ \
  email=test@example.com \
  password=TestPassword123!

# Use token
http GET localhost:8000/api/businesses/ \
  "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Performance

### Check Query Count
```bash
# In settings.py, add:
DEBUG_TOOLBAR = True

# In code:
from django.db import connection
print(len(connection.queries))
```

### Profile Views
```bash
pip install django-silk

# Add to INSTALLED_APPS and urls.py
# Visit http://localhost:8000/silk/
```

## Backup & Restore

### Backup Database
```bash
pg_dump -h host -U user -d database > backup.sql
```

### Restore Database
```bash
psql -h host -U user -d database < backup.sql
```

## Environment Variables

### Load .env file
```bash
# Install python-dotenv
pip install python-dotenv

# In manage.py (already configured):
from dotenv import load_dotenv
load_dotenv()
```

### Check Current Settings
```bash
python3 manage.py shell
>>> from django.conf import settings
>>> settings.DEBUG
>>> settings.DATABASES
>>> settings.INSTALLED_APPS
```

## Git Workflow

### Common Commands
```bash
# Status
git status

# Add all changes
git add .

# Commit
git commit -m "feat: add new feature"

# Push
git push origin main

# Pull latest
git pull origin main
```

### Commit Message Convention
```
feat: New feature
fix: Bug fix
docs: Documentation
style: Formatting
refactor: Code restructuring
test: Adding tests
chore: Maintenance
```

## Quick Troubleshooting

### Port Already in Use
```bash
# Find process using port 8000
lsof -ti:8000

# Kill process
kill -9 $(lsof -ti:8000)
```

### Reset Migrations (CAREFUL!)
```bash
# Delete migration files (keep __init__.py)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# Drop database tables
python3 manage.py flush

# Recreate migrations
python3 manage.py makemigrations
python3 manage.py migrate
```

### Clear Python Cache
```bash
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete
```

---

## 👨‍💻 Development Team

- **Bartosz** - Backend Developer
- **Norbert** - Frontend Developer
