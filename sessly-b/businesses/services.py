from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone as dt_timezone
from typing import Iterable, List, Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.conf import settings
from django.db import transaction
from django.db.models import Q, QuerySet
from django.utils import timezone

from .models import Appointment, Business, BusinessOpeningHour, BusinessService

logger = logging.getLogger(__name__)


class SlotUnavailableError(Exception):
    """Raised when a requested appointment slot is no longer available."""


def get_business_timezone(business: Business) -> ZoneInfo:
    tz_name = business.timezone or settings.TIME_ZONE
    try:
        return ZoneInfo(tz_name)
    except ZoneInfoNotFoundError:
        logger.warning("Nie znaleziono strefy czasowej %s. Uzywam ustawienia domyslnego.", tz_name)
        return ZoneInfo(settings.TIME_ZONE)


def get_business_hours_for_date(business: Business, target_date: date) -> Optional[BusinessOpeningHour]:
    day_index = target_date.weekday()
    try:
        return business.opening_hours.get(day_of_week=day_index)
    except BusinessOpeningHour.DoesNotExist:
        return None


@dataclass(frozen=True)
class AppointmentRange:
    start: datetime
    end: datetime

    def overlaps(self, other_start: datetime, other_end: datetime) -> bool:
        # Overlap if the ranges intersect (inclusive of start, exclusive of end).
        return not (other_end <= self.start or other_start >= self.end)


def _build_existing_ranges(
    appointments: Iterable[Appointment],
    tz: ZoneInfo,
) -> List[AppointmentRange]:
    ranges: List[AppointmentRange] = []
    for appointment in appointments:
        start_local = appointment.start.astimezone(tz)
        end_local = appointment.end.astimezone(tz) + timedelta(minutes=appointment.buffer_minutes)
        ranges.append(AppointmentRange(start=start_local, end=end_local))
    return ranges


def _normalize_time_step(service: BusinessService) -> timedelta:
    step_minutes = service.duration_minutes + service.buffer_minutes
    if step_minutes <= 0:
        return timedelta(minutes=service.duration_minutes or 1)
    return timedelta(minutes=step_minutes)


def _build_local_datetime(target_date: date, target_time: time, tz: ZoneInfo) -> datetime:
    return datetime.combine(target_date, target_time, tzinfo=tz)


def _day_bounds(target_date: date, tz: ZoneInfo) -> tuple[datetime, datetime]:
    day_start = datetime.combine(target_date, time.min, tzinfo=tz)
    day_end = day_start + timedelta(days=1)
    return day_start, day_end


def _active_appointments_qs(business: Business) -> QuerySet[Appointment]:
    return business.appointments.exclude(status=Appointment.Status.CANCELLED)


def calculate_daily_availability(business: Business, service: BusinessService, target_date: date) -> List[time]:
    tz = get_business_timezone(business)
    opening_hours = get_business_hours_for_date(business, target_date)
    if not opening_hours or opening_hours.is_closed:
        return []

    if opening_hours.open_time is None or opening_hours.close_time is None:
        return []

    open_dt = _build_local_datetime(target_date, opening_hours.open_time, tz)
    close_dt = _build_local_datetime(target_date, opening_hours.close_time, tz)
    if open_dt >= close_dt:
        return []

    now_local = timezone.now().astimezone(tz)
    day_start, day_end = _day_bounds(target_date, tz)
    day_start_utc = day_start.astimezone(dt_timezone.utc)
    day_end_utc = day_end.astimezone(dt_timezone.utc)

    existing = (
        _active_appointments_qs(business)
        .filter(
            Q(start__lt=day_end_utc),
            Q(end__gt=day_start_utc),
        )
        .select_related("service")
    )
    existing_ranges = _build_existing_ranges(existing, tz)

    slot_length = timedelta(minutes=service.duration_minutes)
    step = _normalize_time_step(service)

    available_slots: List[time] = []
    current_start = open_dt
    while current_start + slot_length <= close_dt:
        current_end = current_start + slot_length
        if current_end > close_dt:
            break

        if current_start < now_local:
            current_start += step
            continue

        has_conflict = any(r.overlaps(current_start, current_end) for r in existing_ranges)
        if not has_conflict:
            available_slots.append(current_start.timetz().replace(tzinfo=None))

        current_start += step

    return available_slots


def is_slot_available(business: Business, service: BusinessService, start_local: datetime) -> bool:
    tz = get_business_timezone(business)
    start_local = start_local.astimezone(tz)
    target_date = start_local.date()
    opening_hours = get_business_hours_for_date(business, target_date)

    if not opening_hours or opening_hours.is_closed:
        return False

    if opening_hours.open_time is None or opening_hours.close_time is None:
        return False

    open_dt = _build_local_datetime(target_date, opening_hours.open_time, tz)
    close_dt = _build_local_datetime(target_date, opening_hours.close_time, tz)
    end_local = start_local + timedelta(minutes=service.duration_minutes)

    if start_local < open_dt or end_local > close_dt:
        return False

    day_start, day_end = _day_bounds(target_date, tz)
    day_start_utc = day_start.astimezone(dt_timezone.utc)
    day_end_utc = day_end.astimezone(dt_timezone.utc)

    conflicts = (
        _active_appointments_qs(business)
        .filter(
            Q(start__lt=end_local.astimezone(dt_timezone.utc)),
            Q(end__gt=start_local.astimezone(dt_timezone.utc)),
        )
        .select_related("service")
    )
    existing_ranges = _build_existing_ranges(conflicts, tz)
    return not any(r.overlaps(start_local, end_local) for r in existing_ranges)


@transaction.atomic
def create_appointment(
    *,
    business: Business,
    service: BusinessService,
    customer,
    start_local: datetime,
    notes: str = "",
) -> Appointment:
    tz = get_business_timezone(business)
    start_local = start_local.astimezone(tz)
    end_local = start_local + timedelta(minutes=service.duration_minutes)

    if not is_slot_available(business, service, start_local):
        raise SlotUnavailableError("Wybrany termin nie jest juz dostepny.")

    appointment = Appointment(
        business=business,
        service=service,
        customer=customer,
        start=start_local,
        end=end_local,
        buffer_minutes=service.buffer_minutes,
        notes=notes,
    )
    appointment.full_clean()
    appointment.save()
    try:
        from .google_calendar import sync_appointment_with_google
    except ImportError:  # pragma: no cover - opcjonalna zaleznosc
        logger.debug("Integracja z Google Calendar nie jest dostepna.")
    except Exception:  # pragma: no cover - ochronne
        logger.exception("Nie udalo sie zainicjowac synchronizacji z Google Calendar")
    else:
        transaction.on_commit(lambda: sync_appointment_with_google(appointment.id))
    return appointment


def serialize_time_list(values: Iterable[time]) -> List[str]:
    return [value.strftime("%H:%M") for value in values]
