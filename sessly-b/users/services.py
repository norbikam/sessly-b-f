import secrets
from datetime import timedelta
from typing import Tuple

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from django.utils.http import urlencode

from .models import EmailVerification


def _generate_code() -> str:
    return f"{secrets.randbelow(10**6):06d}"


def create_email_verification(user) -> Tuple[EmailVerification, str]:
    """Creates a one-time email verification code for the given user."""
    EmailVerification.objects.filter(user=user, used_at__isnull=True).update(used_at=timezone.now())

    code = _generate_code()
    ttl_minutes = getattr(settings, "EMAIL_VERIFICATION_CODE_TTL_MINUTES", 15)
    expires_at = timezone.now() + timedelta(minutes=ttl_minutes)

    verification = EmailVerification.objects.create(
        user=user,
        code=code,
        expires_at=expires_at,
    )
    return verification, code


def _build_verification_link(user, code: str) -> str:
    base_url = getattr(settings, "FRONTEND_BASE_URL", "").rstrip("/")
    if not base_url:
        return ""
    query = urlencode({"email": user.email, "code": code})
    return f"{base_url}/verify-email?{query}"


def send_verification_email(user, code: str) -> None:
    subject = "Potwierdz swoj adres email"
    ttl_minutes = getattr(settings, "EMAIL_VERIFICATION_CODE_TTL_MINUTES", 15)
    verification_url = _build_verification_link(user, code)

    greeting = f"Czesc {user.first_name}!" if user.first_name else "Czesc!"

    text_lines = [
        greeting,
        "",
        "Dziekujemy za rejestracje w aplikacji Sessly.",
        f"Twoj kod potwierdzenia to: {code}",
        f"Kod wygasa za {ttl_minutes} minut.",
    ]
    if verification_url:
        text_lines.extend(
            [
                "",
                "Mozesz tez potwierdzic adres klikajac w ponizszy link:",
                verification_url,
            ]
        )

    text_body = "\n".join(text_lines)

    html_lines = [
        f"<p>{greeting}</p>",
        "<p>Dziekujemy za rejestracje w aplikacji Sessly.</p>",
        f"<p><strong>Twoj kod potwierdzenia:</strong> {code}</p>",
        f"<p>Kod jest wazny przez {ttl_minutes} minut.</p>",
    ]
    if verification_url:
        html_lines.append(f'<p>Potwierdz adres klikajac w <a href="{verification_url}">ten link</a>.</p>')
    html_body = "\n".join(html_lines)

    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        to=[user.email],
    )
    message.attach_alternative(html_body, "text/html")
    message.send()
