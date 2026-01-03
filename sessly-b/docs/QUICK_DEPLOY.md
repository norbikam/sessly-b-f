# 🚀 Sessly - Quick Deployment Guide

## ✅ Co Jest Gotowe

Twój projekt Sessly jest teraz **production-ready** z następującymi funkcjami:

### Backend Features ✅
- ✅ Pełny system autentykacji (JWT, email verification)
- ✅ Panel dla klientów (przeglądanie i anulowanie rezerwacji)
- ✅ Panel dla właścicieli firm (CRUD firm, usług, godzin otwarcia)
- ✅ Standardowy error handling z kodami błędów
- ✅ System logowania (pliki + konsola kolorowana)
- ✅ Monitoring błędów (Sentry - gotowy do konfiguracji)
- ✅ Rate limiting (ochrona przed atakami)
- ✅ 26 automated tests
- ✅ Paginacja API
- ✅ Google Calendar integration (foundation)

---

## 📋 Checklist Przed Deployment

### 1. Zmienne Środowiskowe (Vercel Dashboard)

Przejdź do **Vercel → Settings → Environment Variables** i dodaj:

#### Wymagane ✅
```bash
# Django Core
DJANGO_ENV=production
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=<WYGENERUJ_DŁUGI_LOSOWY_CIĄG>

# Database (Neon)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Dozwolone domeny
DJANGO_ALLOWED_HOSTS=twoja-domena.vercel.app
CORS_ALLOWED_ORIGINS=https://twoja-domena-frontend.vercel.app

# JWT
JWT_ACCESS_MIN=15
JWT_REFRESH_DAYS=7
```

#### Opcjonalne (ale rekomendowane) ⚠️
```bash
# Email (SendGrid, Mailgun, etc.)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=<TWOJ_API_KEY>
EMAIL_USE_TLS=True
DJANGO_DEFAULT_FROM_EMAIL=Sessly <noreply@sessly.app>

# Sentry (Error Monitoring)
SENTRY_DSN=<TWOJ_SENTRY_DSN>
SENTRY_RELEASE=v1.0.0

# Email Verification
EMAIL_VERIFICATION_ENABLED=True
```

#### Dla rozwoju w przyszłości 🔮
```bash
# Redis (Cache - gdy będzie potrzebny)
REDIS_URL=redis://:<password>@<host>:<port>/0

# Google Calendar (jeśli planujesz używać)
GOOGLE_CALENDAR_ENABLED=True
GOOGLE_SERVICE_ACCOUNT_INFO=<JSON_CREDENTIALS>
GOOGLE_DEFAULT_CALENDAR_ID=<CALENDAR_ID>
```

---

## 🔑 Jak Wygenerować SECRET_KEY

### Opcja 1: Python
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Opcja 2: Online
https://djecrety.ir/

Skopiuj wygenerowany klucz i wstaw do Vercel jako `DJANGO_SECRET_KEY`.

---

## 📧 Konfiguracja Email (SendGrid - Darmowy)

### 1. Zarejestruj się na SendGrid
https://signup.sendgrid.com/ (darmowy plan: 100 emaili/dzień)

### 2. Utwórz API Key
1. Dashboard → Settings → API Keys
2. Create API Key → Full Access
3. Skopiuj klucz (pojawi się tylko raz!)

### 3. Dodaj do Vercel
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=<TWOJ_SENDGRID_API_KEY>
EMAIL_USE_TLS=True
DJANGO_DEFAULT_FROM_EMAIL=Sessly <noreply@twojadomena.pl>
```

### 4. Zweryfikuj domenę (opcjonalnie)
W SendGrid → Settings → Sender Authentication → dodaj swoją domenę

---

## 🔍 Konfiguracja Sentry (Error Monitoring)

### 1. Zarejestruj się na Sentry
https://sentry.io/signup/ (darmowy plan: 5000 errors/miesiąc)

### 2. Utwórz Projekt
1. Create Project → Django
2. Skopiuj DSN (np. `https://abc123@o123.ingest.sentry.io/456`)

### 3. Dodaj do Vercel
```bash
SENTRY_DSN=<TWOJ_SENTRY_DSN>
SENTRY_RELEASE=v1.0.0
```

### 4. Zweryfikuj
Po deploymencie, wywołaj błąd celowo i sprawdź czy pojawił się w Sentry dashboard.

---

## 📊 Konfiguracja Bazy Danych (Neon)

Masz już prawdopodobnie Neon configured, ale upewnij się:

### 1. Sprawdź Connection String
Neon Dashboard → Connection Details → Connection String

Powinien wyglądać tak:
```
postgresql://user:password@ep-xxx.region.aws.neon.tech/neondb?sslmode=require
```

### 2. Dodaj do Vercel jako DATABASE_URL
```bash
DATABASE_URL=postgresql://user:password@ep-xxx.region.aws.neon.tech/neondb?sslmode=require
```

### 3. Uruchom migracje (pierwsz raz deploy)
Vercel automatycznie uruchomi migracje podczas build procesu (patrz `vercel.json`).

---

## 🚀 Deployment Steps

### 1. Push do GitHub
```bash
git add .
git commit -m "Production ready - full features implemented"
git push origin main
```

### 2. Deploy na Vercel
Jeśli masz już połączony GitHub z Vercel:
- Vercel automatycznie wykryje push i rozpocznie deployment
- Sprawdź logi w Vercel Dashboard

Jeśli nie:
```bash
npm i -g vercel
vercel --prod
```

### 3. Sprawdź Deployment
1. Otwórz URL z Vercel
2. Sprawdź `/api/businesses/categories/` - powinno zwrócić listę
3. Sprawdź `/api/users/register/` - spróbuj zarejestrować użytkownika

### 4. Migracje (Jeśli potrzebne)
Jeśli migracje nie uruchomiły się automatycznie:
```bash
# W Vercel Dashboard → Settings → Functions → Add Function
# Utwórz funkcję maintenance z:
vercel env pull .env.production
python manage.py migrate
```

---

## 🧪 Testowanie Po Deployment

### 1. Podstawowe Endpointy
```bash
# Health check
curl https://twoja-domena.vercel.app/api/businesses/categories/

# Rejestracja
curl -X POST https://twoja-domena.vercel.app/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username":"test",
    "email":"test@example.com",
    "password":"Test123!@#",
    "password2":"Test123!@#",
    "first_name":"Test",
    "last_name":"User"
  }'
```

### 2. Sprawdź Logi
Vercel Dashboard → Deployment → Functions → View Logs

### 3. Sprawdź Sentry (jeśli skonfigurowany)
Sentry Dashboard → Projects → Twój Projekt → Issues

---

## 📁 Struktura Projektu (Co Gdzie)

```
sessly-b/
├── backend/               # Konfiguracja Django
│   ├── exceptions.py      # ✨ Kody błędów i custom exceptions
│   ├── responses.py       # ✨ Pomocnicze funkcje dla API responses
│   ├── logging_config.py  # ✨ Kolorowane logi + pliki
│   ├── sentry_config.py   # ✨ Monitoring błędów
│   ├── rate_limiting.py   # ✨ Ochrona przed atakami
│   └── settings.py        # ✨ WSZYSTKO skonfigurowane!
│
├── users/                 # App użytkowników
│   ├── views.py           # ✨ Login, Register, Logout, etc.
│   ├── serializers.py     # ✨ Walidacja z custom exceptions
│   ├── tests.py           # ✨ 14 testów
│   └── urls.py            # ✨ + customer appointments routes
│
├── businesses/            # App rezerwacji
│   ├── views.py           # Publiczne endpointy
│   ├── customer_views.py  # ✨ Panel klienta
│   ├── owner_views.py     # ✨ Panel właściciela
│   ├── serializers.py     # ✨ + BusinessCreateUpdateSerializer
│   ├── services.py        # Logika dostępności
│   ├── tests/
│   │   ├── test_api.py    # 7 testów (oryginalnych)
│   │   └── test_comprehensive.py  # ✨ 12 nowych testów
│   └── urls.py            # ✨ Wszystkie nowe routes
│
├── docs/                  # ✨ Dokumentacja
│   ├── IMPLEMENTATION_PLAN.md   # ✨ Co zrobione + co dalej
│   ├── ERROR_CODES.md           # ✨ Dla frontendu
│   └── DEPLOYMENT.md            # Instrukcje Vercel
│
└── logs/                  # ✨ Automatyczne logowanie
    ├── sessly.log         # Wszystkie logi
    └── errors.log         # Tylko błędy
```

---

## 🎯 Next Steps (Opcjonalne Ulepszenia)

### Tydzień 1-2: Upload Plików
```bash
# Dodaj do requirements.txt
pillow
django-storages[google]  # lub [s3] dla AWS

# Model:
class Business:
    logo = models.ImageField(upload_to='logos/', null=True)
    
# Konfiguracja w Vercel wymaga external storage (GCS/S3)
```

### Tydzień 3-4: Powiadomienia
```bash
# Celery dla async tasks
celery
redis

# Funkcja wysyłania
def send_booking_confirmation(appointment):
    send_mail(
        subject='Potwierdzenie rezerwacji',
        message=f'Witaj {appointment.customer.first_name}...',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[appointment.customer.email]
    )
```

### Tydzień 5-6: Payment (Stripe)
```bash
stripe
dj-stripe

# Docs: https://dj-stripe.dev/
```

---

## 🆘 Troubleshooting

### Błąd: "No module named 'psycopg_c'"
**Rozwiązanie:** To tylko warning, możesz zignorować.

### Błąd: "SECRET_KEY not set"
**Rozwiązanie:** Dodaj `DJANGO_SECRET_KEY` do Vercel environment variables.

### Błąd: "Database connection failed"
**Rozwiązanie:** Sprawdź `DATABASE_URL` w Vercel, upewnij się że zawiera `?sslmode=require`.

### Błąd: "CORS error" z frontendu
**Rozwiązanie:** Dodaj domenę frontendu do `CORS_ALLOWED_ORIGINS`.

### Emails nie wysyłają się
**Rozwiązanie:** 
1. Sprawdź `EMAIL_HOST_PASSWORD` w Vercel
2. Sprawdź logi Vercel czy są błędy SMTP
3. SendGrid: zweryfikuj API key jest "Full Access"

---

## 📞 Support

Jeśli masz pytania:
1. Sprawdź logi w Vercel Dashboard
2. Sprawdź Sentry (jeśli skonfigurowany)
3. Sprawdź `logs/errors.log` lokalnie podczas testów
4. Wszystkie endpointy mają spójne error responses z kodami

---

## 🎉 Gratulacje!

Masz teraz **production-ready** booking system z:
- ✅ 26 testów automatycznych
- ✅ Pełny error handling
- ✅ Logging i monitoring
- ✅ Rate limiting
- ✅ Security best practices
- ✅ CRUD dla firm i usług
- ✅ Panel klienta i właściciela

**Teraz możesz skupić się na frontendzie!** 🚀

Backend gotowy na Vercel + Neon w ~5 minut (zakładając że masz env variables).

---

## 👨‍💻 Development Team

- **Bartosz** - Backend Developer
- **Norbert** - Frontend Developer

---

**Need help?** Check the logs first:
- Vercel: Dashboard → Functions → Logs
- Local: `logs/sessly.log` and `logs/errors.log`
- Sentry: Real-time error tracking
