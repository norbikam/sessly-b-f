# 🚀 Sessly - Quick Start for Developers

**5-minute setup guide to get you coding!**

---

## ⚡ Super Quick Start

```bash
# 1. Clone and enter directory
git clone <your-repo-url>
cd sessly-b

# 2. Run automated setup
./setup.sh

# 3. Edit .env file with your database URL
nano .env

# 4. Start development server
make run
```

**Done!** API is running at http://localhost:8000/api/

---

## 📋 Essential Commands

```bash
make run            # Start server
make test           # Run tests
make shell          # Django shell
make superuser      # Create admin user
make help           # Show all commands
```

Full command reference: [COMMANDS.md](COMMANDS.md)

---

## 🎯 Test the API

### 1. Register a User
```bash
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!",
    "first_name": "Test",
    "last_name": "User"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'
```

Copy the `access` token from the response.

### 3. List Businesses
```bash
curl http://localhost:8000/api/businesses/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 📁 Project Structure

```
sessly-b/
├── backend/              # Django core settings
├── users/                # User auth & profiles
├── businesses/           # Businesses & appointments
├── api/                  # Vercel WSGI handler
├── docs/                 # Documentation
├── logs/                 # Application logs
└── README.md             # Project overview
```

---

## 🔑 Key Files

- **README.md** - Project overview & API docs
- **PROJECT_SUMMARY.md** - Complete project status
- **docs/QUICK_DEPLOY.md** - Deployment guide
- **docs/ERROR_CODES.md** - Error handling reference
- **COMMANDS.md** - All useful commands
- **DEPLOYMENT_CHECKLIST.md** - Deployment checklist

---

## 🧪 Running Tests

```bash
# All tests (26 total)
make test

# Specific app
python3 manage.py test users
python3 manage.py test businesses

# With details
python3 manage.py test --verbosity=2
```

---

## 🐛 Common Issues

### Port Already in Use
```bash
kill -9 $(lsof -ti:8000)
```

### Database Connection Error
Check your `.env` file:
```bash
DATABASE_URL=postgresql://user:pass@host/dbname
```

### Import Errors
Activate virtual environment:
```bash
source venv/bin/activate
```

### Migration Issues
```bash
python3 manage.py migrate
python3 manage.py showmigrations
```

---

## 📚 Learn More

### For Backend Development
1. Read [README.md](README.md) - Overview & API endpoints
2. Check [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - What's implemented
3. Review [docs/IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md) - What's next

### For Frontend Integration
1. See [docs/ERROR_CODES.md](docs/ERROR_CODES.md) - Error handling
2. Check API endpoints in [README.md](README.md)
3. Review authentication flow

### For Deployment
1. Follow [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
2. Configure environment variables
3. Deploy to Vercel

---

## 🎓 Code Examples

### Create a Business (Superuser)
```python
from businesses.models import Business, Category

category = Category.objects.first()
business = Business.objects.create(
    owner=user,
    name="My Salon",
    slug="my-salon",
    category=category,
    description="Best salon in town"
)
```

### Book an Appointment
```bash
POST /api/businesses/my-salon/appointments/
{
  "service": 1,
  "staff_member": 1,
  "appointment_datetime": "2026-01-10T10:00:00Z"
}
```

### Check Availability
```bash
GET /api/businesses/my-salon/availability/?date=2026-01-10
```

---

## 🚀 Production Deployment

```bash
# 1. Configure Vercel
vercel

# 2. Add environment variables in Vercel dashboard:
DJANGO_SECRET_KEY=<generate-new>
DATABASE_URL=<your-neon-db>
DJANGO_ALLOWED_HOSTS=*.vercel.app

# 3. Deploy
vercel --prod
```

Detailed guide: [docs/QUICK_DEPLOY.md](docs/QUICK_DEPLOY.md)

---

## 💡 Tips

- Use `make help` to see all available commands
- Check `logs/app.log` for debugging
- Run `make check-deploy` before deploying
- Read error codes in [docs/ERROR_CODES.md](docs/ERROR_CODES.md)
- Use Django admin at http://localhost:8000/admin/

---

## 🆘 Need Help?

1. Check documentation in `docs/` folder
2. Review [COMMANDS.md](COMMANDS.md) for useful commands
3. Read [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines
4. Check existing issues/discussions

---

## ✅ Checklist for First Day

- [ ] Clone repository
- [ ] Run `./setup.sh`
- [ ] Configure `.env` file
- [ ] Create superuser (`make superuser`)
- [ ] Start server (`make run`)
- [ ] Access admin panel (http://localhost:8000/admin/)
- [ ] Run tests (`make test`)
- [ ] Test API with curl/Postman
- [ ] Read README.md
- [ ] Read PROJECT_SUMMARY.md

---

**Ready to code! 🎉**

If you completed the checklist above, you're all set to start developing!

---

## 👨‍💻 Development Team

- **Bartosz** - Lead Developer
- **Norbert** - Backend Developer

---

*Built with Django REST Framework 🐍*
