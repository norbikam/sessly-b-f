# 🗓️ Sessly - Booking & Reservation System

**Production-ready Django REST API for managing appointments and reservations.**

Perfect for hairdressers, doctors, beauty salons, spas, fitness centers, and any service-based business.

---

## ✨ Features

### For Customers
- 📝 User registration with email verification
- 🔐 JWT authentication
- 🔍 Browse businesses by category and location
- 📅 Check real-time availability
- ⏰ Book appointments
- 📋 View appointment history
- ❌ Cancel appointments
- ⭐ Manage favorite businesses

### For Business Owners
- 🏢 Create and manage business profile
- 💼 Add and manage services
- ⏰ Set opening hours (with bulk update)
- 👥 Manage staff members
- 📊 View business statistics
- ✅ Confirm/cancel customer appointments
- 📈 Track appointments and revenue

### Technical Features
- 🔒 Production-ready security (HTTPS, CORS, CSRF protection)
- 📧 Email system (SendGrid/Mailgun ready)
- 🐛 Error monitoring (Sentry integration)
- 📝 Comprehensive logging
- 🚦 Rate limiting
- ✅ 26 automated tests
- 📄 Paginated API responses
- 🌐 Google Calendar integration (foundation)
- 🎯 Standardized error codes for frontend

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL (or Neon serverless)
- Vercel account (for deployment)

### Local Development

```bash
# Clone repository
git clone <your-repo-url>
cd sessly-b

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your DATABASE_URL and other settings

# Run migrations
python3 manage.py migrate

# Create superuser
python3 manage.py createsuperuser

# Run development server
python3 manage.py runserver
```

API will be available at http://localhost:8000/api/

---

## 📚 API Documentation

### Authentication
```bash
POST /api/users/register/          # Register new user
POST /api/users/login/             # Login (get JWT tokens)
POST /api/users/token/refresh/     # Refresh access token
POST /api/users/logout/            # Logout (blacklist token)
POST /api/users/verify-email/      # Verify email with code
```

### Businesses (Public)
```bash
GET  /api/businesses/categories/                      # List categories
GET  /api/businesses/                                 # List businesses
GET  /api/businesses/{slug}/                          # Business details
GET  /api/businesses/{slug}/availability/             # Check availability
POST /api/businesses/{slug}/appointments/             # Create appointment
```

### Customer Panel
```bash
GET  /api/users/appointments/                         # My appointments
GET  /api/users/appointments/{id}/                    # Appointment details
POST /api/users/appointments/{id}/cancel/             # Cancel appointment
GET  /api/users/favorites/                            # Favorite businesses
POST /api/users/favorites/{business_id}/              # Toggle favorite
```

### Business Owner Panel
```bash
# Business Management
GET    /api/businesses/my-business/                   # List my businesses
POST   /api/businesses/my-business/                   # Create business
GET    /api/businesses/my-business/{id}/stats/        # Business statistics

# Services
GET    /api/businesses/{slug}/services/               # List services
POST   /api/businesses/{slug}/services/               # Create service
PUT    /api/businesses/{slug}/services/{id}/          # Update service
DELETE /api/businesses/{slug}/services/{id}/          # Delete service

# Opening Hours
GET    /api/businesses/{slug}/opening-hours/          # List hours
POST   /api/businesses/{slug}/opening-hours/bulk-update/  # Update all week
PUT    /api/businesses/{slug}/opening-hours/{id}/     # Update single day

# Appointments
POST   /api/businesses/{slug}/appointments/{id}/confirm/   # Confirm
POST   /api/businesses/{slug}/appointments/{id}/cancel/    # Cancel
```

Full API documentation: [docs/ERROR_CODES.md](docs/ERROR_CODES.md)

---

## 🏗️ Architecture

```
Backend (Django REST Framework)
├── User Management (JWT Auth)
├── Business Profiles
├── Services & Pricing
├── Availability Calculation
├── Appointment Booking
├── Email Notifications
└── Google Calendar Sync
```

**Database:** PostgreSQL (Neon serverless)  
**Deployment:** Vercel  
**Monitoring:** Sentry  
**Email:** SendGrid/Mailgun  

---

## 🧪 Testing

```bash
# Run all tests
python3 manage.py test

# Run specific app tests
python3 manage.py test users
python3 manage.py test businesses

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

**Current test coverage:** 26 tests covering critical functionality

---

## 🔧 Configuration

### Required Environment Variables

```bash
DJANGO_SECRET_KEY=<generate-long-random-string>
DATABASE_URL=postgresql://user:pass@host/db
DJANGO_ALLOWED_HOSTS=your-domain.vercel.app
```

### Optional (Recommended)

```bash
# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=<sendgrid-api-key>

# Sentry
SENTRY_DSN=<your-sentry-dsn>

# Google Calendar
GOOGLE_CALENDAR_ENABLED=True
GOOGLE_SERVICE_ACCOUNT_INFO=<json-credentials>
```

See [docs/QUICK_DEPLOY.md](docs/QUICK_DEPLOY.md) for detailed setup instructions.

---

## 📦 Deployment

### Deploy to Vercel

1. Push to GitHub
2. Import project in Vercel
3. Add environment variables
4. Deploy!

```bash
vercel --prod
```

Detailed deployment guide: [docs/QUICK_DEPLOY.md](docs/QUICK_DEPLOY.md)

---

## 📖 Documentation

- **[Implementation Plan](docs/IMPLEMENTATION_PLAN.md)** - What's implemented and what's next
- **[Error Codes](docs/ERROR_CODES.md)** - Frontend integration guide
- **[Deployment Guide](docs/QUICK_DEPLOY.md)** - Step-by-step deployment
- **[Original Deployment](docs/DEPLOYMENT.md)** - Vercel deployment notes

---

## 🛠️ Tech Stack

- **Django 6.0** - Web framework
- **Django REST Framework** - API framework
- **PostgreSQL** - Database
- **JWT** - Authentication
- **Sentry** - Error monitoring
- **SendGrid** - Email delivery
- **Google Calendar API** - Calendar integration
- **Vercel** - Hosting platform

---

## 🎯 Roadmap

### ✅ Completed
- User authentication & authorization
- Business management (CRUD)
- Appointment booking system
- Real-time availability
- Email verification
- Error handling with codes
- Comprehensive logging
- Rate limiting
- 26 automated tests

### 🚧 In Progress
- File uploads (business logos, galleries)
- Email notifications for appointments
- SMS notifications

### 📋 Planned
- Reviews & ratings system
- Payment integration (Stripe/PayU)
- Multi-language support (i18n)
- Mobile push notifications
- Advanced analytics

---

## 👨‍💻 Development Team

- **Bartosz** - Backend Developer
- **Norbert** - Frontend Developer

---

## 📄 License

This project is licensed under the MIT License.

---

## 🆘 Support

- Check [docs/QUICK_DEPLOY.md](docs/QUICK_DEPLOY.md) for common issues
- Review error logs in `logs/` directory
- Check Sentry dashboard for production errors
- API returns standardized error codes (see [docs/ERROR_CODES.md](docs/ERROR_CODES.md))

---

## 👨‍💻 Author

Built with ❤️ for service-based businesses

**Status:** Production Ready ✅

---

Made with Django REST Framework 🐍
