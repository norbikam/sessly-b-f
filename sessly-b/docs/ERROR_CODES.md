# Kody Błędów API - Dokumentacja dla Frontendu

## Sposób Użycia

Wszystkie odpowiedzi API mają teraz standardowy format:

### Sukces
```json
{
  "success": true,
  "data": { ... }
}
```

### Błąd
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Komunikat po polsku dla użytkownika",
    "details": {
      "field_name": ["Błąd dla konkretnego pola"]
    }
  }
}
```

---

## Lista Kodów Błędów

### Autentykacja i Autoryzacja

| Kod | Znaczenie | Status HTTP | Kiedy występuje |
|-----|-----------|-------------|-----------------|
| `INVALID_CREDENTIALS` | Nieprawidłowe dane logowania | 401 | Błędny email lub hasło przy logowaniu |
| `WRONG_PASSWORD` | Nieprawidłowe hasło | 401 | Błędne stare hasło przy zmianie |
| `EMAIL_ALREADY_EXISTS` | Email już istnieje | 400 | Próba rejestracji z istniejącym emailem |
| `USERNAME_ALREADY_EXISTS` | Nazwa użytkownika zajęta | 400 | Próba rejestracji z zajętą nazwą |
| `EMAIL_NOT_VERIFIED` | Email niezweryfikowany | 403 | Logowanie przed weryfikacją emaila |
| `INVALID_TOKEN` | Nieprawidłowy token | 401 | Token JWT jest nieprawidłowy |
| `TOKEN_EXPIRED` | Token wygasł | 401 | Token JWT wygasł |
| `UNAUTHORIZED` | Brak autoryzacji | 401 | Brak tokenu lub nieprawidłowy token |
| `PERMISSION_DENIED` | Brak uprawnień | 403 | Próba dostępu do zasobu bez uprawnień |

### Weryfikacja Email

| Kod | Znaczenie | Status HTTP | Kiedy występuje |
|-----|-----------|-------------|-----------------|
| `INVALID_VERIFICATION_CODE` | Nieprawidłowy kod | 400 | Błędny kod weryfikacyjny |
| `VERIFICATION_CODE_EXPIRED` | Kod wygasł | 400 | Kod weryfikacyjny starszy niż 15 minut |
| `VERIFICATION_CODE_USED` | Kod już użyty | 400 | Próba użycia tego samego kodu drugi raz |

### Rezerwacje

| Kod | Znaczenie | Status HTTP | Kiedy występuje |
|-----|-----------|-------------|-----------------|
| `SLOT_UNAVAILABLE` | Termin niedostępny | 400 | Próba rezerwacji zajętego terminu |
| `PAST_BOOKING` | Rezerwacja w przeszłości | 400 | Próba rezerwacji terminu z przeszłości |
| `SERVICE_NOT_FOUND` | Usługa nie istnieje | 404 | Podano ID nieistniejącej usługi |
| `BUSINESS_NOT_FOUND` | Firma nie istnieje | 404 | Podano slug nieistniejącej firmy |
| `APPOINTMENT_NOT_FOUND` | Rezerwacja nie istnieje | 404 | Podano ID nieistniejącej rezerwacji |

### Walidacja

| Kod | Znaczenie | Status HTTP | Kiedy występuje |
|-----|-----------|-------------|-----------------|
| `VALIDATION_ERROR` | Błąd walidacji | 400 | Ogólny błąd walidacji pól formularza |
| `INVALID_INPUT` | Nieprawidłowe dane | 400 | Błędny format danych wejściowych |
| `REQUIRED_FIELD` | Brak wymaganego pola | 400 | Nie przesłano wymaganego pola |

### Ogólne

| Kod | Znaczenie | Status HTTP | Kiedy występuje |
|-----|-----------|-------------|-----------------|
| `NOT_FOUND` | Nie znaleziono | 404 | Zasób nie istnieje |
| `SERVER_ERROR` | Błąd serwera | 500 | Wewnętrzny błąd serwera |
| `BAD_REQUEST` | Błędne żądanie | 400 | Nieprawidłowe żądanie HTTP |

---

## Przykłady Obsługi we Frontendzie

### React/React Native

```jsx
const handleRegister = async (formData) => {
  try {
    const response = await fetch('/api/users/register/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData),
    });
    
    const data = await response.json();
    
    if (!data.success) {
      // Obsłuż błąd według kodu
      switch (data.error.code) {
        case 'EMAIL_ALREADY_EXISTS':
          setError('email', 'Ten adres email jest już zarejestrowany');
          break;
        case 'USERNAME_ALREADY_EXISTS':
          setError('username', 'Ta nazwa użytkownika jest zajęta');
          break;
        case 'VALIDATION_ERROR':
          // Obsłuż błędy walidacji dla konkretnych pól
          Object.entries(data.error.details || {}).forEach(([field, errors]) => {
            setError(field, errors[0]);
          });
          break;
        default:
          // Pokaż ogólny komunikat błędu
          Alert.alert('Błąd', data.error.message);
      }
      return;
    }
    
    // Sukces - użytkownik utworzony
    const { user, access, refresh } = data.data;
    await saveTokens(access, refresh);
    navigation.navigate('Home');
    
  } catch (error) {
    Alert.alert('Błąd', 'Nie można połączyć się z serwerem');
  }
};

const handleLogin = async (username, password) => {
  try {
    const response = await fetch('/api/users/login/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });
    
    const data = await response.json();
    
    if (!data.success) {
      switch (data.error.code) {
        case 'INVALID_CREDENTIALS':
          Alert.alert('Błąd', 'Nieprawidłowy email lub hasło');
          break;
        case 'EMAIL_NOT_VERIFIED':
          navigation.navigate('VerifyEmail', { email: username });
          break;
        default:
          Alert.alert('Błąd', data.error.message);
      }
      return;
    }
    
    // Sukces
    const { user, access, refresh } = data;
    await saveTokens(access, refresh);
    navigation.navigate('Home');
    
  } catch (error) {
    Alert.alert('Błąd', 'Nie można połączyć się z serwerem');
  }
};

const handleBooking = async (bookingData) => {
  try {
    const response = await fetch(`/api/businesses/${slug}/appointments/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
      },
      body: JSON.stringify(bookingData),
    });
    
    const data = await response.json();
    
    if (!data.success) {
      switch (data.error.code) {
        case 'SLOT_UNAVAILABLE':
          Alert.alert('Termin niedostępny', 'Ten termin został już zarezerwowany');
          // Odśwież dostępne terminy
          refreshAvailability();
          break;
        case 'PAST_BOOKING':
          Alert.alert('Błąd', 'Nie możesz zarezerwować terminu w przeszłości');
          break;
        case 'SERVICE_NOT_FOUND':
          Alert.alert('Błąd', 'Wybrana usługa nie istnieje');
          break;
        case 'UNAUTHORIZED':
          // Token wygasł - odśwież lub wyloguj
          await refreshAccessToken();
          break;
        default:
          Alert.alert('Błąd', data.error.message);
      }
      return;
    }
    
    // Sukces
    Alert.alert('Sukces', 'Rezerwacja została utworzona');
    navigation.navigate('MyAppointments');
    
  } catch (error) {
    Alert.alert('Błąd', 'Nie można połączyć się z serwerem');
  }
};
```

### Axios Interceptor (Rekomendowane)

```javascript
import axios from 'axios';

// Konfiguracja axios
const api = axios.create({
  baseURL: 'https://twoja-api.vercel.app',
});

// Interceptor dla odpowiedzi
api.interceptors.response.use(
  (response) => {
    // Zwróć dane jeśli sukces
    if (response.data.success) {
      return response.data;
    }
    // Jeśli nie success, rzuć błąd
    return Promise.reject(response.data.error);
  },
  (error) => {
    if (error.response) {
      // Serwer odpowiedział z błędem
      const errorData = error.response.data.error;
      return Promise.reject(errorData);
    }
    // Błąd sieci
    return Promise.reject({
      code: 'NETWORK_ERROR',
      message: 'Nie można połączyć się z serwerem',
    });
  }
);

// Użycie
const register = async (formData) => {
  try {
    const data = await api.post('/api/users/register/', formData);
    // data zawiera już { user, access, refresh }
    return data;
  } catch (error) {
    // error zawiera { code, message, details? }
    if (error.code === 'EMAIL_ALREADY_EXISTS') {
      throw new Error('Ten email jest już zarejestrowany');
    }
    throw new Error(error.message);
  }
};
```

---

## Walidacja Pól Formularza

Gdy `error.code === 'VALIDATION_ERROR'`, pole `error.details` zawiera obiekt z błędami dla konkretnych pól:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Hasła nie są identyczne",
    "details": {
      "password": ["Hasła nie są identyczne"],
      "email": ["Ten adres email jest już zarejestrowany"]
    }
  }
}
```

Obsługa:
```javascript
if (error.code === 'VALIDATION_ERROR' && error.details) {
  // Iteruj po błędach i pokaż przy odpowiednich polach
  Object.entries(error.details).forEach(([fieldName, errors]) => {
    const errorMessage = Array.isArray(errors) ? errors[0] : errors;
    setFieldError(fieldName, errorMessage);
  });
}
```

---

## Best Practices

1. **Zawsze sprawdzaj `success` field:**
   ```javascript
   if (!response.data.success) {
     // Obsłuż błąd
   }
   ```

2. **Używaj kodu błędu, nie komunikatu:**
   - Kod jest stały i można go łatwo obsługiwać w kodzie
   - Komunikat może się zmienić i jest po polsku (dla użytkownika)

3. **Obsługuj specyficzne kody:**
   - Nie polegaj tylko na `catch (error)` - obsłuż konkretne kody
   - `EMAIL_ALREADY_EXISTS` → pokaż przy polu email
   - `SLOT_UNAVAILABLE` → odśwież dostępne terminy

4. **Odświeżaj tokeny automatycznie:**
   ```javascript
   if (error.code === 'TOKEN_EXPIRED') {
     await refreshAccessToken();
     // Powtórz żądanie
   }
   ```

5. **Loguj błędy dla debugowania:**
   ```javascript
   if (!data.success) {
     console.error('API Error:', data.error.code, data.error.message);
   }
   ```

---

## Testowanie

Możesz testować kody błędów lokalnie:

```bash
# EMAIL_ALREADY_EXISTS
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"istniejacy@email.com","username":"test","password":"Test123!@#","password2":"Test123!@#"}'

# INVALID_CREDENTIALS
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"wrongpassword"}'

# SLOT_UNAVAILABLE
curl -X POST http://localhost:8000/api/businesses/salon-test/appointments/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"service_id":"uuid","date":"2026-01-05","start_time":"10:00"}'
```

---

## Wsparcie

Jeśli napotkasz kod błędu, którego nie ma w tej dokumentacji, sprawdź:
- [backend/exceptions.py](../backend/exceptions.py) - wszystkie kody błędów
- Logi serwera w Vercel
- Sentry (jeśli skonfigurowane)

---

## 👨‍💻 Development Team

- **Bartosz** - Backend Developer
- **Norbert** - Frontend Developer
