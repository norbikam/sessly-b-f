import uuid
from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Business(models.Model):
    class Category(models.TextChoices):
        HAIRDRESSER = "hairdresser", "Fryzjer"
        DOCTOR = "doctor", "Lekarz"
        BEAUTY = "beauty", "Salon pieknosci"
        SPA = "spa", "SPA"
        FITNESS = "fitness", "Fitness"
        OTHER = "other", "Inne"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    category = models.CharField(
        max_length=32, choices=Category.choices, default=Category.OTHER
    )
    description = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=32, blank=True)
    website_url = models.URLField(blank=True)
    nip = models.CharField(max_length=13, blank=True, help_text="Numer Identyfikacji Podatkowej (NIP)")
    timezone = models.CharField(max_length=64, default="Europe/Warsaw")
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=128)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=64, default="Polska")
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    google_calendar_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:  # pragma: no cover - repr
        return self.name


class BusinessStaff(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(
        Business, on_delete=models.CASCADE, related_name="staff_members"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="business_staff_positions",
    )
    is_manager = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("business", "user")
        ordering = ("user__username",)

    def __str__(self) -> str:  # pragma: no cover - repr
        return f"{self.user.username} - {self.business.name}"


class BusinessOpeningHour(models.Model):
    class Weekday(models.IntegerChoices):
        MONDAY = 0, "Poniedzialek"
        TUESDAY = 1, "Wtorek"
        WEDNESDAY = 2, "Sroda"
        THURSDAY = 3, "Czwartek"
        FRIDAY = 4, "Piatek"
        SATURDAY = 5, "Sobota"
        SUNDAY = 6, "Niedziela"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(
        Business, on_delete=models.CASCADE, related_name="opening_hours"
    )
    day_of_week = models.PositiveSmallIntegerField(choices=Weekday.choices)
    is_closed = models.BooleanField(default=False)
    open_time = models.TimeField(blank=True, null=True)
    close_time = models.TimeField(blank=True, null=True)

    class Meta:
        unique_together = ("business", "day_of_week")
        ordering = ("business", "day_of_week")

    def clean(self):
        if self.is_closed:
            return

        if self.open_time is None or self.close_time is None:
            raise ValidationError(
                "Musisz podac godziny otwarcia i zamkniecia lub oznaczyc dzien jako nieczynny."
            )

        if self.open_time >= self.close_time:
            raise ValidationError("Godzina zamkniecia musi byc po godzinie otwarcia.")

    def __str__(self) -> str:  # pragma: no cover - repr
        return f"{self.business.name} {self.get_day_of_week_display()}"


class BusinessService(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(
        Business, on_delete=models.CASCADE, related_name="services"
    )
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField()
    buffer_minutes = models.PositiveIntegerField(default=0)
    price_amount = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    price_currency = models.CharField(max_length=3, default="PLN")
    is_active = models.BooleanField(default=True)
    color = models.CharField(max_length=16, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:  # pragma: no cover - repr
        return f"{self.name} ({self.business.name})"

    @property
    def total_slot_minutes(self) -> int:
        return self.duration_minutes + self.buffer_minutes


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Oczekujące"
        CONFIRMED = "confirmed", "Potwierdzone"
        CANCELLED = "cancelled", "Anulowane"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(
        Business, on_delete=models.CASCADE, related_name="appointments"
    )
    staff = models.ForeignKey(
        BusinessStaff,
        on_delete=models.CASCADE,
        related_name="appointments",
        null=True,
        blank=True,
    )
    service = models.ForeignKey(
        BusinessService, on_delete=models.CASCADE, related_name="appointments"
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.PENDING
    )
    start = models.DateTimeField()
    end = models.DateTimeField()
    buffer_minutes = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)
    google_event_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-start",)
        indexes = [
            models.Index(fields=["business", "start"]),
            models.Index(fields=["customer", "start"]),
        ]

    def __str__(self) -> str:  # pragma: no cover - repr
        return f"{self.service.name} - {self.start.isoformat()}"

    def clean(self):
        if self.start >= self.end:
            raise ValidationError("Czas zakonczenia musi byc po czasie rozpoczecia.")

        expected_end = self.start + timedelta(minutes=self.service.duration_minutes)
        if expected_end != self.end:
            raise ValidationError("Czas zakonczenia musi odpowiadac dlugosci uslugi.")
