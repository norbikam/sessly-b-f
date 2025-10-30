from __future__ import annotations

from datetime import time
from decimal import Decimal
from typing import Any, Dict, Iterable, List

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from businesses.models import Business, BusinessOpeningHour, BusinessService


BusinessPayload = Dict[str, Any]


BUSINESS_FIXTURES: List[BusinessPayload] = [
    {
        "slug": "glow-studio-warszawa",
        "defaults": {
            "name": "Glow Studio Warszawa",
            "category": Business.Category.BEAUTY,
            "description": (
                "Nowoczesny salon beauty w sercu Warszawy. Oferujemy kompleksowe zabiegi pielęgnacyjne "
                "dla twarzy i ciała, wykorzystując sprawdzone produkty i techniki."
            ),
            "email": "kontakt@glowstudio.pl",
            "phone_number": "+48 511 234 567",
            "website_url": "https://glowstudio.pl",
            "timezone": "Europe/Warsaw",
            "address_line1": "ul. Mokotowska 58",
            "address_line2": "lok. 3",
            "city": "Warszawa",
            "postal_code": "00-543",
            "country": "Polska",
            "latitude": Decimal("52.224130"),
            "longitude": Decimal("21.013610"),
        },
        "services": [
            {
                "name": "Rytual Glow Signature",
                "description": (
                    "Kompleksowy zabieg pielęgnacyjny łączący oczyszczanie, masaż twarzy i intensywne "
                    "nawilżenie. Idealny przed ważnym wydarzeniem."
                ),
                "duration_minutes": 75,
                "buffer_minutes": 10,
                "price_amount": Decimal("249.00"),
                "price_currency": "PLN",
                "color": "#8B5CF6",
            },
            {
                "name": "Lifting rzęs & brwi",
                "description": (
                    "Zabieg laminacji rzęs i brwi podkreślający naturalne piękno oka. Efekt utrzymuje się do "
                    "6 tygodni."
                ),
                "duration_minutes": 60,
                "buffer_minutes": 10,
                "price_amount": Decimal("179.00"),
                "price_currency": "PLN",
                "color": "#6366F1",
            },
            {
                "name": "Masaż relaksacyjny całego ciała",
                "description": (
                    "Delikatny masaż aromaterapeutyczny pomagający rozluźnić napięcia i zredukować stres."
                ),
                "duration_minutes": 90,
                "buffer_minutes": 15,
                "price_amount": Decimal("289.00"),
                "price_currency": "PLN",
                "color": "#14B8A6",
            },
        ],
        "opening_hours": [
            {
                "day_of_week": BusinessOpeningHour.Weekday.MONDAY,
                "is_closed": False,
                "open_time": time(hour=9),
                "close_time": time(hour=19),
            },
            {
                "day_of_week": BusinessOpeningHour.Weekday.TUESDAY,
                "is_closed": False,
                "open_time": time(hour=9),
                "close_time": time(hour=19),
            },
            {
                "day_of_week": BusinessOpeningHour.Weekday.WEDNESDAY,
                "is_closed": False,
                "open_time": time(hour=9),
                "close_time": time(hour=19),
            },
            {
                "day_of_week": BusinessOpeningHour.Weekday.THURSDAY,
                "is_closed": False,
                "open_time": time(hour=9),
                "close_time": time(hour=20),
            },
            {
                "day_of_week": BusinessOpeningHour.Weekday.FRIDAY,
                "is_closed": False,
                "open_time": time(hour=9),
                "close_time": time(hour=20),
            },
            {
                "day_of_week": BusinessOpeningHour.Weekday.SATURDAY,
                "is_closed": False,
                "open_time": time(hour=10),
                "close_time": time(hour=16),
            },
            {
                "day_of_week": BusinessOpeningHour.Weekday.SUNDAY,
                "is_closed": True,
                "open_time": None,
                "close_time": None,
            },
        ],
    },
    {
        "slug": "atelier-fryzjerskie-bielany",
        "defaults": {
            "name": "Atelier Fryzjerskie Bielany",
            "category": Business.Category.HAIRDRESSER,
            "description": (
                "Autorski salon fryzjerski specjalizujący się w personalizowanych strzyżeniach i koloryzacjach. "
                "Co godzinę dostępne są nowe terminy, abyś mógł umówić wizytę wtedy, kiedy potrzebujesz."
            ),
            "email": "rezerwacje@atelierfryzjerskie.pl",
            "phone_number": "+48 512 890 321",
            "website_url": "https://atelierfryzjerskie.pl",
            "timezone": "Europe/Warsaw",
            "address_line1": "ul. Kasprowicza 68",
            "address_line2": "",
            "city": "Warszawa",
            "postal_code": "01-871",
            "country": "Polska",
            "latitude": Decimal("52.275400"),
            "longitude": Decimal("20.947200"),
        },
        "services": [
            {
                "name": "Strzyżenie damskie premium",
                "description": (
                    "Indywidualna konsultacja, regeneracja włosów oraz stylizacja w cenie. Idealne na metamorfozę."
                ),
                "duration_minutes": 60,
                "buffer_minutes": 0,
                "price_amount": Decimal("180.00"),
                "price_currency": "PLN",
                "color": "#EF4444",
            },
            {
                "name": "Strzyżenie męskie & stylizacja",
                "description": "Precyzyjne cięcie z wykończeniem i poradą pielęgnacyjną.",
                "duration_minutes": 45,
                "buffer_minutes": 15,
                "price_amount": Decimal("120.00"),
                "price_currency": "PLN",
                "color": "#F59E0B",
            },
            {
                "name": "Koloryzacja total look",
                "description": (
                    "Kompleksowa koloryzacja z tonowaniem i regeneracją Olaplex. W cenie konsultacja kolorystyczna."
                ),
                "duration_minutes": 120,
                "buffer_minutes": 15,
                "price_amount": Decimal("420.00"),
                "price_currency": "PLN",
                "color": "#6366F1",
            },
        ],
        "opening_hours": [
            {
                "day_of_week": BusinessOpeningHour.Weekday.MONDAY,
                "is_closed": False,
                "open_time": time(hour=8),
                "close_time": time(hour=18),
            },
            {
                "day_of_week": BusinessOpeningHour.Weekday.TUESDAY,
                "is_closed": False,
                "open_time": time(hour=8),
                "close_time": time(hour=18),
            },
            {
                "day_of_week": BusinessOpeningHour.Weekday.WEDNESDAY,
                "is_closed": False,
                "open_time": time(hour=8),
                "close_time": time(hour=18),
            },
            {
                "day_of_week": BusinessOpeningHour.Weekday.THURSDAY,
                "is_closed": False,
                "open_time": time(hour=8),
                "close_time": time(hour=19),
            },
            {
                "day_of_week": BusinessOpeningHour.Weekday.FRIDAY,
                "is_closed": False,
                "open_time": time(hour=8),
                "close_time": time(hour=19),
            },
            {
                "day_of_week": BusinessOpeningHour.Weekday.SATURDAY,
                "is_closed": False,
                "open_time": time(hour=8),
                "close_time": time(hour=16),
            },
            {
                "day_of_week": BusinessOpeningHour.Weekday.SUNDAY,
                "is_closed": True,
                "open_time": None,
                "close_time": None,
            },
        ],
    },
]


class Command(BaseCommand):
    help = "Creates or updates demo businesses with services and opening hours."

    def add_arguments(self, parser):
        parser.add_argument(
            "--slug",
            help="If provided, only the business with this slug will be seeded.",
        )

    def handle(self, *args, **options):
        target_slug: str | None = options.get("slug")
        fixtures = BUSINESS_FIXTURES
        if target_slug:
            fixtures = [fixture for fixture in fixtures if fixture["slug"] == target_slug]
            if not fixtures:
                raise CommandError(f"Brak konfiguracji dla sluga '{target_slug}'.")

        for fixture in fixtures:
            self._seed_business(fixture)

        self.stdout.write(self.style.SUCCESS(f"Seedowanie zakonczone. Przetworzono {len(fixtures)} biznes(y)."))

    def _seed_business(self, payload: BusinessPayload) -> None:
        slug = payload["slug"]
        defaults = payload["defaults"]
        services: Iterable[dict] = payload.get("services", [])
        opening_hours: Iterable[dict] = payload.get("opening_hours", [])

        with transaction.atomic():
            business, created = Business.objects.update_or_create(
                slug=slug,
                defaults=defaults,
            )
            action = "Utworzono" if created else "Zaktualizowano"
            self.stdout.write(self.style.SUCCESS(f"{action} biznes: {business.name} ({business.slug})"))

            service_names: List[str] = []
            for service in services:
                name = service["name"]
                defaults = {key: value for key, value in service.items() if key != "name"}
                BusinessService.objects.update_or_create(
                    business=business,
                    name=name,
                    defaults=defaults,
                )
                service_names.append(name)

            deleted_services, _ = business.services.exclude(name__in=service_names).delete()
            if deleted_services:
                self.stdout.write(f"Usunieto {deleted_services} nieaktualnych uslug.")

            self.stdout.write(f"Aktywne uslugi ({len(service_names)}):")
            for name in service_names:
                self.stdout.write(f"  - {name}")

            tracked_days: List[int] = []
            for entry in opening_hours:
                day = int(entry["day_of_week"])
                defaults = {
                    "is_closed": entry["is_closed"],
                    "open_time": entry["open_time"] if not entry["is_closed"] else None,
                    "close_time": entry["close_time"] if not entry["is_closed"] else None,
                }
                BusinessOpeningHour.objects.update_or_create(
                    business=business,
                    day_of_week=day,
                    defaults=defaults,
                )
                tracked_days.append(day)

            deleted_hours, _ = business.opening_hours.exclude(day_of_week__in=tracked_days).delete()
            if deleted_hours:
                self.stdout.write(f"Usunieto {deleted_hours} nieaktualnych wpisow godzin otwarcia.")

            self.stdout.write(self.style.SUCCESS("Godziny otwarcia zaktualizowane."))
            self.stdout.write(self.style.SUCCESS(f"Biznes {business.slug} gotowy do uzycia."))
