from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from functools import lru_cache
from typing import Optional

from django.conf import settings

try:
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:  # pragma: no cover - optional dependency
    Credentials = None  # type: ignore[assignment]
    build = None  # type: ignore[assignment]
    HttpError = Exception  # type: ignore[assignment]

logger = logging.getLogger(__name__)

CALENDAR_SCOPES = ["https://www.googleapis.com/auth/calendar"]


@dataclass(frozen=True)
class CalendarConfig:
    enabled: bool
    default_calendar_id: Optional[str]
    service_account_info: Optional[dict]
    service_account_file: Optional[str]


def get_calendar_config() -> CalendarConfig:
    info = getattr(settings, "GOOGLE_SERVICE_ACCOUNT_INFO", None)
    file_path = getattr(settings, "GOOGLE_SERVICE_ACCOUNT_FILE", None)
    parsed_info = None
    if info:
        try:
            parsed_info = json.loads(info)
        except json.JSONDecodeError as exc:  # pragma: no cover - guardrail
            logger.error("Niepoprawny JSON w GOOGLE_SERVICE_ACCOUNT_INFO: %s", exc)
    return CalendarConfig(
        enabled=getattr(settings, "GOOGLE_CALENDAR_ENABLED", False),
        default_calendar_id=getattr(settings, "GOOGLE_DEFAULT_CALENDAR_ID", None),
        service_account_info=parsed_info,
        service_account_file=file_path,
    )


def is_enabled() -> bool:
    config = get_calendar_config()
    return bool(config.enabled and (config.service_account_info or config.service_account_file) and build and Credentials)


@lru_cache(maxsize=1)
def _build_credentials() -> Optional["Credentials"]:
    if not is_enabled():
        return None

    config = get_calendar_config()
    if Credentials is None:
        return None

    if config.service_account_info:
        return Credentials.from_service_account_info(config.service_account_info, scopes=CALENDAR_SCOPES)

    if config.service_account_file:
        try:
            return Credentials.from_service_account_file(config.service_account_file, scopes=CALENDAR_SCOPES)
        except OSError as exc:  # pragma: no cover - guardrail
            logger.error("Nie udalo sie wczytac pliku Google Service Account: %s", exc)

    return None


@lru_cache(maxsize=1)
def _build_service():
    credentials = _build_credentials()
    if not credentials or build is None:
        return None

    return build("calendar", "v3", credentials=credentials, cache_discovery=False)


def _resolve_calendar_id(business) -> Optional[str]:
    if business.google_calendar_id:
        return business.google_calendar_id
    config = get_calendar_config()
    return config.default_calendar_id


def _build_event_summary(appointment) -> str:
    customer = appointment.customer
    customer_name = customer.get_full_name().strip() or customer.username or customer.email or "Klient"
    return f"{appointment.service.name} - {customer_name}"


def _build_event_location(business) -> str:
    parts = [business.address_line1]
    if business.address_line2:
        parts.append(business.address_line2)
    city_line = f"{business.postal_code} {business.city}".strip()
    if city_line:
        parts.append(city_line)
    if business.country:
        parts.append(business.country)
    return ", ".join(filter(None, parts))


def _build_event_body(appointment) -> dict:
    business = appointment.business
    notes = appointment.notes or appointment.service.description or ""
    attendees = []
    if appointment.customer.email:
        attendees.append(
            {
                "email": appointment.customer.email,
                "displayName": appointment.customer.get_full_name() or appointment.customer.username,
            }
        )

    return {
        "summary": _build_event_summary(appointment),
        "description": notes,
        "location": _build_event_location(business),
        "start": {
            "dateTime": appointment.start.isoformat(),
            "timeZone": business.timezone,
        },
        "end": {
            "dateTime": appointment.end.isoformat(),
            "timeZone": business.timezone,
        },
        "attendees": attendees,
        "reminders": {
            "useDefault": True,
        },
    }


def sync_appointment_with_google(appointment_id):
    if not is_enabled():
        return None

    service = _build_service()
    if service is None:
        logger.debug("Brak uslugi Google Calendar - pomijam synchronizacje")
        return None

    from .models import Appointment  # lokalny import zeby uniknac cykli

    try:
        appointment = (
            Appointment.objects.select_related("business", "service", "customer")
            .filter(pk=appointment_id)
            .get()
        )
    except Appointment.DoesNotExist:
        logger.warning("Nie znaleziono wizyty %s do synchronizacji z Google Calendar", appointment_id)
        return None

    calendar_id = _resolve_calendar_id(appointment.business)
    if not calendar_id:
        logger.info(
            "Brak zdefiniowanego kalendarza Google dla biznesu %s - pomijam synchronizacje",
            appointment.business.name,
        )
        return None

    event_body = _build_event_body(appointment)
    try:
        if appointment.google_event_id:
            event = (
                service.events()
                .update(calendarId=calendar_id, eventId=appointment.google_event_id, body=event_body, sendUpdates="all")
                .execute()
            )
        else:
            event = (
                service.events()
                .insert(calendarId=calendar_id, body=event_body, sendUpdates="all")
                .execute()
            )
    except HttpError as exc:  # pragma: no cover - network edge
        logger.error("Blad Google Calendar: %s", exc)
        return None

    google_event_id = event.get("id")
    if google_event_id and google_event_id != appointment.google_event_id:
        Appointment.objects.filter(pk=appointment.pk).update(google_event_id=google_event_id)
    return google_event_id
