# 🎯 Final Deployment Checklist

**Before deploying Sessly to production, complete all items below.**

---

## ✅ Pre-Deployment Checklist

### 1. Environment Configuration
- [ ] Generate strong `DJANGO_SECRET_KEY`
  ```bash
  python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```
- [ ] Set `DJANGO_DEBUG=False` in production
- [ ] Configure `DJANGO_ALLOWED_HOSTS` with your domain
- [ ] Set up PostgreSQL database (Neon recommended)
- [ ] Configure `DATABASE_URL` properly

### 2. Email Service
- [ ] Sign up for SendGrid (https://sendgrid.com/)
- [ ] Generate API key
- [ ] Set `EMAIL_HOST_PASSWORD` in Vercel
- [ ] Set `DEFAULT_FROM_EMAIL` to your domain email
- [ ] Test email sending

### 3. Error Monitoring
- [ ] Sign up for Sentry (https://sentry.io/)
- [ ] Create new Django project in Sentry
- [ ] Copy `SENTRY_DSN`
- [ ] Set `SENTRY_DSN` in Vercel environment variables
- [ ] Set `SENTRY_ENVIRONMENT=production`
- [ ] Test error reporting

### 4. Security Settings
- [ ] Verify `SECURE_SSL_REDIRECT=True` in production
- [ ] Verify `SESSION_COOKIE_SECURE=True` in production
- [ ] Verify `CSRF_COOKIE_SECURE=True` in production
- [ ] Set `SECURE_HSTS_SECONDS=31536000` (1 year)
- [ ] Configure CORS allowed origins

### 5. Database
- [ ] Run all migrations
  ```bash
  python3 manage.py migrate
  ```
- [ ] Create superuser for admin access
  ```bash
  python3 manage.py createsuperuser
  ```
- [ ] Verify database backups are configured
- [ ] Test database connection

### 6. Static Files
- [ ] Collect static files
  ```bash
  python3 manage.py collectstatic --noinput
  ```
- [ ] Verify static files are accessible

### 7. Testing
- [ ] Run all tests locally
  ```bash
  make test
  ```
- [ ] Verify 26/26 tests pass
- [ ] Run deployment check
  ```bash
  python3 manage.py check --deploy
  ```
- [ ] Fix any WARNINGS or ERRORS

### 8. Code Quality
- [ ] All Python files compile without errors
- [ ] No hardcoded secrets in code
- [ ] All environment variables in `.env.example`
- [ ] `.gitignore` excludes sensitive files
- [ ] Code follows PEP 8 standards

### 9. Documentation
- [ ] README.md is up to date
- [ ] API endpoints documented
- [ ] Environment variables documented
- [ ] Deployment guide reviewed

### 10. Vercel Setup
- [ ] Create Vercel account
- [ ] Install Vercel CLI
  ```bash
  npm i -g vercel
  ```
- [ ] Link project to Vercel
  ```bash
  vercel link
  ```
- [ ] Add all environment variables in Vercel dashboard
- [ ] Configure custom domain (optional)

---

## 🚀 Deployment Steps

### Step 1: Final Local Testing
```bash
# Activate virtual environment
source venv/bin/activate

# Run tests
make test

# Check deployment readiness
make check-deploy

# Collect static files
python3 manage.py collectstatic --noinput
```

### Step 2: Commit and Push
```bash
# Add all changes
git add .

# Commit
git commit -m "feat: production ready v1.0.0"

# Push to GitHub
git push origin main
```

### Step 3: Configure Vercel
```bash
# Login to Vercel
vercel login

# Deploy to preview
vercel

# Review preview deployment
# Test all endpoints
```

### Step 4: Set Environment Variables
In Vercel Dashboard → Settings → Environment Variables:

**Required:**
```
DJANGO_SECRET_KEY=<your-generated-secret>
DATABASE_URL=postgresql://user:pass@host/dbname
DJANGO_ALLOWED_HOSTS=your-app.vercel.app
DJANGO_DEBUG=False
```

**Recommended:**
```
SENTRY_DSN=<your-sentry-dsn>
SENTRY_ENVIRONMENT=production
EMAIL_HOST_PASSWORD=<sendgrid-api-key>
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
FRONTEND_URL=https://your-frontend.vercel.app
```

### Step 5: Production Deployment
```bash
# Deploy to production
vercel --prod

# Wait for deployment to complete
# Note the production URL
```

### Step 6: Database Migration
```bash
# SSH into Vercel or run migration via API
# Or use Vercel CLI with database connection
vercel env pull .env.production
python3 manage.py migrate --settings=backend.settings
```

### Step 7: Create Superuser
```bash
# Access production database
# Create superuser
python3 manage.py createsuperuser
```

---

## ✅ Post-Deployment Verification

### Test All Endpoints
- [ ] User Registration: `POST /api/users/register/`
- [ ] User Login: `POST /api/users/login/`
- [ ] Email Verification: `POST /api/users/verify-email/`
- [ ] List Businesses: `GET /api/businesses/`
- [ ] Business Details: `GET /api/businesses/{slug}/`
- [ ] Create Appointment: `POST /api/businesses/{slug}/appointments/`
- [ ] List My Appointments: `GET /api/users/appointments/`

### Check Admin Panel
- [ ] Access admin: `https://your-app.vercel.app/admin/`
- [ ] Login with superuser
- [ ] Verify all models visible
- [ ] Create test data

### Monitor Errors
- [ ] Open Sentry dashboard
- [ ] Trigger test error
- [ ] Verify error appears in Sentry
- [ ] Check error details

### Check Logs
- [ ] View Vercel logs
- [ ] Check for errors
- [ ] Verify requests logging

### Test Email
- [ ] Trigger email verification
- [ ] Check email delivery
- [ ] Verify email content
- [ ] Test email links

### Performance Testing
- [ ] Test API response times
- [ ] Check database query performance
- [ ] Verify static files load
- [ ] Test under load (optional)

---

## 🔧 Environment Variables Reference

### Production (.env for Vercel)
```bash
# Django Core
DJANGO_SECRET_KEY=<50+ character random string>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-app.vercel.app,your-custom-domain.com

# Database (Neon)
DATABASE_URL=postgresql://user:password@host.neon.tech/dbname?sslmode=require

# Email (SendGrid)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Sentry
SENTRY_DSN=https://xxxxx@oxxxxx.ingest.sentry.io/xxxxx
SENTRY_ENVIRONMENT=production

# CORS
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app,https://www.yourdomain.com

# Frontend
FRONTEND_URL=https://your-frontend.vercel.app

# Redis (optional - for production caching)
REDIS_URL=redis://default:password@host:6379

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
```

---

## 🐛 Common Deployment Issues

### Issue: 500 Internal Server Error
**Solution:**
1. Check Vercel logs
2. Verify `DJANGO_SECRET_KEY` is set
3. Check `DATABASE_URL` connection
4. Review Sentry errors

### Issue: Static Files Not Loading
**Solution:**
1. Run `python3 manage.py collectstatic`
2. Verify `vercel.json` build command
3. Check `STATIC_ROOT` in settings

### Issue: Database Connection Failed
**Solution:**
1. Verify `DATABASE_URL` format
2. Check database is accessible
3. Verify SSL mode (`?sslmode=require`)
4. Test connection locally

### Issue: CORS Errors
**Solution:**
1. Add frontend URL to `CORS_ALLOWED_ORIGINS`
2. Verify `django-cors-headers` installed
3. Check middleware order

### Issue: Email Not Sending
**Solution:**
1. Verify SendGrid API key
2. Check email backend configuration
3. Test with `python3 manage.py shell`
4. Review SendGrid dashboard

---

## 📊 Monitoring Setup

### Sentry Configuration
1. Projects → Create Project → Django
2. Copy DSN
3. Add to Vercel environment variables
4. Deploy
5. Trigger test error
6. Verify in Sentry dashboard

### Vercel Analytics
1. Enable in Vercel dashboard
2. View deployment analytics
3. Monitor function duration
4. Check bandwidth usage

### Database Monitoring (Neon)
1. Access Neon dashboard
2. View connection stats
3. Monitor query performance
4. Set up alerts

---

## 🎉 Success Criteria

Your deployment is successful when:
- ✅ All API endpoints respond correctly
- ✅ User registration and login work
- ✅ Email verification emails are delivered
- ✅ Appointments can be created and managed
- ✅ Admin panel is accessible
- ✅ Errors appear in Sentry
- ✅ No 500 errors in production
- ✅ Response times < 500ms
- ✅ Database queries are optimized
- ✅ Static files load correctly

---

## 📞 Support

If you encounter issues:
1. Check Vercel logs
2. Review Sentry errors
3. Check database connection
4. Review documentation
5. Check GitHub issues

---

## 🎯 Next Steps After Deployment

1. **Frontend Development**
   - Connect frontend to API
   - Implement error handling
   - Add loading states

2. **Optional Features**
   - File uploads (S3/GCS)
   - Email notifications
   - Payment integration

3. **Monitoring**
   - Set up uptime monitoring
   - Configure alerts
   - Review analytics

4. **Optimization**
   - Add Redis caching
   - Optimize database queries
   - Enable compression

---

**Ready to deploy! 🚀**

Follow this checklist step by step and your Sessly backend will be live in ~30 minutes.

---

## 👨‍💻 Development Team

- **Bartosz** - Lead Developer
- **Norbert** - Backend Developer

---

Good luck! 🎉
