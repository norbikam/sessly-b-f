# Plan Rozwoju Projektu Sessly

## Status Implementacji ✅

### Etap 1: Naprawione Błędy Krytyczne ✅
- [x] Poprawiono pole `favorite_businesses` w modelu User (było `favorite_business`)
- [x] Naprawiono `BusinessStaffSerializer` - dodano brakujące pola (`user_id`, `username`, `is_manager`)
- [x] Dodano brakujące dekoratory `@action` w `BusinessAppointmentViewSet`

### Etap 2: Standardowy System Obsługi Błędów ✅
- [x] Utworzono `backend/exceptions.py` z klasami wyjątków i kodami błędów
- [x] Zaimplementowano `custom_exception_handler` dla spójnych odpowiedzi API
- [x] Dodano kody błędów dla frontendu (EMAIL_ALREADY_EXISTS, WRONG_PASSWORD, etc.)
- [x] Utworzono `backend/responses.py` z pomocniczymi funkcjami

### Etap 3: Konfiguracja Produkcyjna ✅
- [x] Dodano bezpieczne domyślne ustawienia dla produkcji
- [x] `DEBUG = False` domyślnie w produkcji
- [x] `SECRET_KEY` wymagany w środowisku produkcyjnym
- [x] Dodano paginację (20 elementów na stronę)
- [x] Handler wyjątków w `REST_FRAMEWORK` settings

### Etap 4: Panel dla Klientów ✅
- [x] Utworzono `businesses/customer_views.py` z ViewSetami dla klientów
- [x] Endpoint `GET /api/users/appointments/` - lista rezerwacji użytkownika
- [x] Endpoint `GET /api/users/appointments/{id}/` - szczegóły rezerwacji
- [x] Endpoint `POST /api/users/appointments/{id}/cancel/` - anulowanie rezerwacji
- [x] Filtrowanie rezerwacji po statusie i czasie (upcoming/past)
- [x] Walidacja - nie można anulować rezerwacji z przeszłości

### Etap 5: Panel dla Właścicieli Firm ✅
- [x] Utworzono `businesses/owner_views.py` z pełnym CRUD dla właścicieli
- [x] **BusinessManagementViewSet** - zarządzanie biznesem:
  - `GET /api/businesses/my-business/` - lista firm właściciela
  - `POST /api/businesses/my-business/` - utworzenie firmy
  - `PUT/PATCH /api/businesses/my-business/{id}/` - edycja firmy
  - `DELETE /api/businesses/my-business/{id}/` - usunięcie firmy
  - `GET /api/businesses/my-business/{id}/stats/` - statystyki firmy
- [x] **BusinessServiceViewSet** - zarządzanie usługami:
  - `GET /api/businesses/{slug}/services/` - lista usług
  - `POST /api/businesses/{slug}/services/` - utworzenie usługi
  - `PUT/PATCH /api/businesses/{slug}/services/{id}/` - edycja usługi
  - `DELETE /api/businesses/{slug}/services/{id}/` - usunięcie usługi
- [x] **BusinessOpeningHoursViewSet** - zarządzanie godzinami otwarcia:
  - `GET /api/businesses/{slug}/opening-hours/` - lista godzin
  - `POST /api/businesses/{slug}/opening-hours/` - utworzenie godzin
  - `PUT/PATCH /api/businesses/{slug}/opening-hours/{id}/` - edycja godzin
  - `POST /api/businesses/{slug}/opening-hours/bulk-update/` - hurtowa aktualizacja
  - `DELETE /api/businesses/{slug}/opening-hours/{id}/` - usunięcie godzin
- [x] Utworzono `BusinessCreateUpdateSerializer` dla tworzenia/edycji firm

### Etap 6: System Logowania ✅
- [x] Utworzono `backend/logging_config.py` z kolorowanym formatowaniem
- [x] Automatyczne logowanie do plików (`logs/sessly.log`, `logs/errors.log`)
- [x] Rotacja logów (15MB, 10 backupów)
- [x] Pomocnicze funkcje: `log_user_action`, `log_business_action`, `log_appointment_action`
- [x] Dodano logging do kluczowych operacji (rejestracja, anulowanie rezerwacji)
- [x] Osobne loggery dla `users`, `businesses`, `django.request`

### Etap 7: Monitoring Błędów (Sentry) ✅
- [x] Utworzono `backend/sentry_config.py` z konfiguracją Sentry
- [x] Automatyczna inicjalizacja gdy `SENTRY_DSN` jest ustawiony
- [x] Integracja z Django i systemem logowania
- [x] Funkcje pomocnicze: `set_user_context`, `capture_exception`, `capture_message`
- [x] Before-send hook do filtrowania eventów
- [x] Performance monitoring (traces)

### Etap 8: Rate Limiting ✅
- [x] Utworzono `backend/rate_limiting.py` z dekoratorami
- [x] Konfiguracja cache (LocalMemory dla dev, Redis dla prod)
- [x] Pre-configured rate limiters:
  - `rate_limit_auth` - 5/minutę (login/logout)
  - `rate_limit_registration` - 3/godzinę (rejestracja)
  - `rate_limit_api` - 100/minutę (API ogólne)
  - `rate_limit_booking` - 10/minutę (rezerwacje)
- [x] Automatyczne pobieranie IP z proxy headers

### Etap 9: Comprehensive Tests ✅
- [x] Utworzono `users/tests.py` z kompleksowymi testami:
  - **UserRegistrationTests** (4 testy) - rejestracja, duplikat email, słabe hasło
  - **UserLoginTests** (3 testy) - sukces, błędne hasło, nieistniejący użytkownik
  - **EmailVerificationTests** (3 testy) - sukces, błędny kod, wygasły kod
  - **ChangePasswordTests** (3 testy) - sukces, błędne stare hasło, niezgodne nowe
  - **LogoutTests** (1 test) - sukces
  - **Total: 14 testów dla users**
- [x] Rozszerzono `businesses/tests/test_comprehensive.py`:
  - **CustomerAppointmentTests** (4 testy) - lista, filtrowanie, anulowanie
  - **BusinessOwnerTests** (6 testów) - CRUD firm, usług, godzin otwarcia, statystyki
  - **AppointmentConfirmationTests** (2 testy) - potwierdzanie/anulowanie przez właściciela
  - **Total: 12 nowych testów dla businesses**

---

## Nowe Endpointy API

### Dla Klientów (Users)
```
GET    /api/users/appointments/                    - Lista moich rezerwacji
GET    /api/users/appointments/{id}/               - Szczegóły rezerwacji
POST   /api/users/appointments/{id}/cancel/        - Anuluj rezerwację
```

### Dla Właścicieli Firm (Business Owners)
```
# Zarządzanie firmą
GET    /api/businesses/my-business/                - Lista moich firm
POST   /api/businesses/my-business/                - Utwórz firmę
GET    /api/businesses/my-business/{id}/           - Szczegóły firmy
PUT    /api/businesses/my-business/{id}/           - Aktualizuj firmę
PATCH  /api/businesses/my-business/{id}/           - Częściowa aktualizacja
DELETE /api/businesses/my-business/{id}/           - Usuń firmę
GET    /api/businesses/my-business/{id}/stats/     - Statystyki firmy

# Zarządzanie usługami
GET    /api/businesses/{slug}/services/            - Lista usług
POST   /api/businesses/{slug}/services/            - Utwórz usługę
GET    /api/businesses/{slug}/services/{id}/       - Szczegóły usługi
PUT    /api/businesses/{slug}/services/{id}/       - Aktualizuj usługę
PATCH  /api/businesses/{slug}/services/{id}/       - Częściowa aktualizacja
DELETE /api/businesses/{slug}/services/{id}/       - Usuń usługę

# Zarządzanie godzinami otwarcia
GET    /api/businesses/{slug}/opening-hours/                      - Lista godzin
POST   /api/businesses/{slug}/opening-hours/                      - Utwórz godziny
GET    /api/businesses/{slug}/opening-hours/{id}/                 - Szczegóły
PUT    /api/businesses/{slug}/opening-hours/{id}/                 - Aktualizuj
DELETE /api/businesses/{slug}/opening-hours/{id}/                 - Usuń
POST   /api/businesses/{slug}/opening-hours/bulk-update/          - Hurtowa aktualizacja (cały tydzień)

# Zarządzanie rezerwacjami (już istniało, poprawione)
GET    /api/businesses/{slug}/appointments/                       - Lista rezerwacji
POST   /api/businesses/{slug}/appointments/{id}/confirm/          - Potwierdź
POST   /api/businesses/{slug}/appointments/{id}/cancel/           - Anuluj
```

---

## Format Odpowiedzi API

### Sukces
```json
{
  "success": true,
  "data": {...},
  "message": "Opcjonalna wiadomość"
}
```

### Błąd
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Czytelny komunikat",
    "details": {
      "field_name": ["Błąd walidacji pola"]
    }
  }
}
```

---

## Co Należy Jeszcze Zrobić

### Priorytet WYSOKI 🔴 (Opcjonalnie - większość już zrobiona!)

#### 1. ~~Panel dla Właścicieli Firm~~ ✅ ZROBIONE
#### 2. ~~Panel dla Klientów~~ ✅ ZROBIONE  
#### 3. ~~System Testów~~ ✅ ZROBIONE (26 testów total)
#### 4. ~~Logging i Monitoring~~ ✅ ZROBIONE

#### 5. Dopełnienie Sentry (Wymaga API Key) ⚠️
**MUSISZ ZROBIĆ:**
1. Zarejestruj się na https://sentry.io (darmowy plan)
2. Utwórz nowy projekt Django
3. Skopiuj DSN (Data Source Name)
4. Ustaw zmienną `SENTRY_DSN` w Vercel
5. Deploy - błędy będą automatycznie raportowane!

**Plik gotowy:** `backend/sentry_config.py` - tylko wstaw DSN!

---

### Priorytet ŚREDNI 🟡

#### 5. Panel dla Pracowników
**Status:** Brak implementacji

**Do zrobienia:**
- [ ] Endpoint do kalendarza pracownika:
  - `GET /api/staff/calendar/` - rezerwacje przypisane do pracownika
- [ ] Endpoint do zarządzania dostępnością:
  - `GET/POST /api/staff/availability/` - ustaw niedostępność
- [ ] Uprawnienia dla pracowników (`IsStaff` permission)

#### 6. Powiadomienia
**Status:** Wysyłanie email tylko przy rejestracji

**Do zrobienia:**
- [ ] Email przy nowej rezerwacji (klient + właściciel)
- [ ] Email przy potwierdzeniu rezerwacji
- [ ] Email przy anulowaniu
- [ ] Przypomnienie 24h przed wizytą
- [ ] SMS (opcjonalnie, integracja z Twilio)

**Nowy plik:** `businesses/notifications.py`

#### 7. Upload Plików
**Status:** Brak

**Do zrobienia:**
- [ ] Logo firmy
- [ ] Zdjęcia galerii firmy
- [ ] Avatar użytkownika
- [ ] Integracja z S3/Cloudinary dla przechowywania
- [ ] Walidacja rozmiaru i typu pliku

**Dodać do modeli:**
```python
# businesses/models.py
class Business:
    logo = models.ImageField(upload_to='business_logos/', null=True, blank=True)
    gallery_images = models.ManyToManyField('BusinessImage')

class BusinessImage:
    business = models.ForeignKey(Business)
    image = models.ImageField(upload_to='business_gallery/')
    order = models.PositiveIntegerField(default=0)
```

#### 8. Wyszukiwanie i Filtrowanie
**Status:** Podstawowe wyszukiwanie istnieje

**Do zrobienia:**
- [ ] Wyszukiwanie pełnotekstowe (PostgreSQL full-text search)
- [ ] Filtrowanie według:
  - Dystans od lokalizacji użytkownika
  - Ocena (gdy będzie system ocen)
  - Dostępność w określonym czasie
  - Zakres cenowy
- [ ] Sortowanie wyników

#### 9. Cache
**Status:** Brak

**Do zrobienia:**
- [ ] Redis dla cache'owania:
  - Lista firm (cache na 5 minut)
  - Godziny otwarcia (cache na 1 godzinę)
  - Dostępne usługi (cache na 15 minut)
- [ ] Cache invalidation przy zmianach

**Konfiguracja:**
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': get_env('REDIS_URL', 'redis://127.0.0.1:6379/1'),
    }
}
```

---

### Priorytet NISKI 🟢

#### 10. System Ocen i Opinii
**Status:** Brak

**Nowy model:**
```python
class Review(models.Model):
    business = models.ForeignKey(Business, related_name='reviews')
    customer = models.ForeignKey(User)
    appointment = models.OneToOneField(Appointment)  # tylko po wizycie
    rating = models.PositiveSmallIntegerField()  # 1-5
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### 11. Płatności
**Status:** Brak

**Opcje:**
- Stripe (międzynarodowe)
- PayU/Przelewy24 (Polska)
- PayPal

**Do zaimplementowania:**
- [ ] Przedpłata przy rezerwacji
- [ ] Zwroty przy anulowaniu
- [ ] Raporty finansowe dla właścicieli

#### 12. Multi-język (i18n)
**Status:** Obecnie tylko Polski

**Do zrobienia:**
- [ ] Konfiguracja Django i18n
- [ ] Tłumaczenia EN/PL
- [ ] Endpoint do zmiany języka

#### 13. Mobile Push Notifications
**Status:** Brak

**Wymaga:**
- Firebase Cloud Messaging (FCM)
- Przechowywanie device tokens
- Wysyłanie powiadomień przy rezerwacjach

---

## Przykłady Użycia Nowego Systemu Błędów

### Frontend - Obsługa Błędów

```javascript
// Rejestracja
try {
  const response = await fetch('/api/users/register/', {
    method: 'POST',
    body: JSON.stringify(formData)
  });
  const data = await response.json();
  
  if (!data.success) {
    // Specyficzne obsługiwanie błędów
    switch(data.error.code) {
      case 'EMAIL_ALREADY_EXISTS':
        showError('emailField', 'Ten email jest już zarejestrowany');
        break;
      case 'USERNAME_ALREADY_EXISTS':
        showError('usernameField', 'Ta nazwa użytkownika jest zajęta');
        break;
      case 'VALIDATION_ERROR':
        // Pokaż błędy dla konkretnych pól
        Object.entries(data.error.details).forEach(([field, errors]) => {
          showError(field, errors[0]);
        });
        break;
      default:
        showError('general', data.error.message);
    }
  } else {
    // Sukces
    navigateToHome(data.data);
  }
} catch (error) {
  showError('general', 'Błąd połączenia z serwerem');
}

// Logowanie
try {
  const response = await fetch('/api/users/login/', {
    method: 'POST',
    body: JSON.stringify({ username, password })
  });
  const data = await response.json();
  
  if (!data.success) {
    switch(data.error.code) {
      case 'INVALID_CREDENTIALS':
        showError('Nieprawidłowy email lub hasło');
        break;
      case 'EMAIL_NOT_VERIFIED':
        showEmailVerificationPrompt();
        break;
      default:
        showError(data.error.message);
    }
  }
} catch (error) {
  showError('Błąd połączenia');
}
```

---

## Kolejne Kroki - Rekomendacje

### Tydzień 1-2: Podstawowe Funkcjonalności ✅
1. ✅ Napraw krytyczne błędy
2. ✅ Zaimplementuj standardowy system błędów
3. ⏳ Napisz testy dla `users` app
4. ⏳ Dodaj endpointy dla klientów (moje rezerwacje, anulowanie)

### Tydzień 3-4: Panel Właściciela
1. Dodaj CRUD dla biznesów
2. Dodaj CRUD dla usług
3. Dodaj zarządzanie godzinami otwarcia
4. Dodaj podstawowe statystyki

### Tydzień 5-6: Produkcja
1. Skonfiguruj Sentry dla monitoringu
2. Dodaj logowanie
3. Rozszerz testy (cel >80%)
4. Dodaj dokumentację API (Swagger)
5. Skonfiguruj Redis dla cache
6. Deploy na Vercel + sprawdź wszystkie env variables

---

## Zmienne Środowiskowe dla Produkcji

Utwórz plik `.env.production` lub ustaw w Vercel:

```bash
# Django
DJANGO_ENV=production
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=<WYGENERUJ_SILNY_KLUCZ>
DJANGO_ALLOWED_HOSTS=twoja-domena.vercel.app,twoja-domena.pl

# Database (Neon)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# JWT
JWT_ACCESS_MIN=15
JWT_REFRESH_DAYS=7

# Email (np. SendGrid, Mailgun)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=<SENDGRID_API_KEY>
EMAIL_USE_TLS=True
DJANGO_DEFAULT_FROM_EMAIL=Sessly <noreply@twojaaplikacja.pl>

# CORS
CORS_ALLOWED_ORIGINS=https://twoja-domena.pl,https://www.twoja-domena.pl

# Google Calendar (opcjonalnie)
GOOGLE_CALENDAR_CREDENTIALS=<JSON_CREDENTIALS>

# Sentry (monitoring błędów)
SENTRY_DSN=<TWOJ_SENTRY_DSN>

# Redis (cache)
REDIS_URL=redis://:<password>@<host>:<port>/0
```

---

## Kontakt przy Problemach

Jeśli masz pytania podczas implementacji:
1. Sprawdź logi w Vercel/Sentry
2. Uruchom testy lokalnie: `python manage.py test`
3. Sprawdź dokumentację DRF: https://www.django-rest-framework.org/

---

## 👨‍💻 Development Team

- **Bartosz** - Backend Developer
- **Norbert** - Frontend Developer

---

Powodzenia! 🚀
