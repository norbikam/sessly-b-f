# Deployment Guide

This project is prepared for a Vercel + Neon stack with Expo acting as the front end.

## Environment variables

Set the following variables both locally (for development) and on Vercel (for production):

| Variable | Description |
|----------|-------------|
| `DJANGO_SECRET_KEY` | Django secret key. Generate a long random string (`python -c "import secrets; print(secrets.token_urlsafe(64))"`). |
| `DJANGO_DEBUG` | `True` locally, `False` in production. |
| `DJANGO_ALLOWED_HOSTS` | Comma separated hostnames. On Vercel include `your-project.vercel.app` and custom domains. |
| `DATABASE_URL` | Provided by Neon. Format: `postgresql://USER:PASSWORD@HOST:PORT/DB_NAME`. Append `?sslmode=require`. |
| `DATABASE_CONN_MAX_AGE` | Optional. Keep at `600` unless you know you need a different value. |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | SMTP credentials from your email provider (Resend, SendGrid, Brevo, etc). |
| `EMAIL_USE_TLS` / `EMAIL_USE_SSL` | Configure according to your provider. Usually `EMAIL_USE_TLS=True`, `EMAIL_USE_SSL=False`. |
| `DJANGO_DEFAULT_FROM_EMAIL` | Default sender, e.g. `Sessly <no-reply@sessly.app>`. |
| `FRONTEND_BASE_URL` | Base URL for the Expo/Next.js front end used to build verification links (e.g. `https://sessly.app`). |
| `EMAIL_VERIFICATION_ENABLED` | Set to `True` (default) to require email confirmation. Temporary `False` skips sending codes. |
| `CORS_ALLOWED_ORIGINS` | Extra comma separated origins allowed to call the API. Include the Expo dev tunnel if needed. |
| `CSRF_TRUSTED_ORIGINS` | Required when you expose Django admin behind HTTPS. Include `https://your-domain`. |
| `JWT_ACCESS_MIN` / `JWT_REFRESH_DAYS` | Optional overrides for token lifetimes. |

## Neon database setup

1. Create a new project in [Neon](https://neon.tech).
2. Under **Connection details**, copy the `psql` connection string and convert it to the URL form:
   ```
   postgresql://USER:PASSWORD@HOST/DB_NAME?sslmode=require
   ```
3. Set this string as `DATABASE_URL` locally in `.env` and in the Vercel dashboard.
4. Run migrations locally:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   python manage.py migrate
   python manage.py createsuperuser
   ```
5. For production migrations use the Vercel CLI:
   ```bash
   vercel --prod
   vercel env pull .env.production.local
   # Edit .env.production.local if needed
   vercel run python manage.py migrate
   ```

## Email verification

* An email with a six digit code and a deep link is sent via the configured SMTP backend.
* Make sure the provider you use allows sending transactional email (Resend, SendGrid, Mailjet, Brevo, etc).
* Double check that `DEFAULT_FROM_EMAIL` and SPF/DKIM records are configured for good deliverability.

## Deploying on Vercel

1. Install dependencies locally:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
2. Log in to Vercel and link the repository:
   ```bash
   vercel login
   vercel link
   ```
3. Push the code to a Git repository and let Vercel build, or trigger a manual deploy with:
   ```bash
   vercel --prod
   ```
4. The `vercel.json` file configures a Python 3.11 runtime, installs dependencies, runs `collectstatic`, and exposes Django through a serverless WSGI handler (`api/index.py`).
5. After every deploy, run migrations against Neon:
   ```bash
   vercel run python manage.py migrate
   ```

## Expo front end integration

* Calls to the API must point to `https://your-project.vercel.app/api/...` once deployed.
* During local development, keep running Django on `http://127.0.0.1:8000` and Expo on its default port. CORS is already configured for `localhost`, `127.0.0.1`, and the Expo web preview (`19006`).
* If you use Expo tunnels or LAN addresses, append them to `CORS_ALLOWED_ORIGINS`.
