from datetime import time, timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from businesses.models import Appointment, Business, BusinessOpeningHour, BusinessService

User = get_user_model()


class BusinessAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="jan",
            email="jan@example.com",
            password="strong-password-123",
            first_name="Jan",
            last_name="Kowalski",
        )

        self.business = Business.objects.create(
            name="Testowy Salon",
            slug="testowy-salon",
            category=Business.Category.HAIRDRESSER,
            description="Salon testowy do rezerwacji.",
            email="kontakt@testowy-salon.pl",
            phone_number="+48 987 654 321",
            timezone="Europe/Warsaw",
            address_line1="ul. Testowa 1",
            city="Warszawa",
            postal_code="00-001",
            country="Polska",
        )

        for day in range(6):
            BusinessOpeningHour.objects.create(
                business=self.business,
                day_of_week=day,
                is_closed=False,
                open_time=time(9, 0),
                close_time=time(17, 0),
            )
        BusinessOpeningHour.objects.create(business=self.business, day_of_week=6, is_closed=True)

        self.service = BusinessService.objects.create(
            business=self.business,
            name="Strzyzenie testowe",
            description="Testowa usluga fryzjerska.",
            duration_minutes=60,
            buffer_minutes=0,
            price_amount=120,
            price_currency="PLN",
        )

    def test_list_businesses(self):
        url = reverse("business-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(item["slug"] == self.business.slug for item in response.data))

    def test_retrieve_business_details(self):
        url = reverse("business-detail", args=[self.business.slug])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["slug"], self.business.slug)
        self.assertGreaterEqual(len(response.data["services"]), 1)
        self.assertEqual(response.data["services"][0]["duration_minutes"], self.service.duration_minutes)

    def test_check_availability(self):
        target_date = timezone.localdate() + timedelta(days=1)
        url = reverse("business-availability", args=[self.business.slug])
        response = self.client.get(
            url,
            {
                "date": target_date.isoformat(),
                "service_id": str(self.service.id),
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("09:00", response.data["slots"])

    def test_create_appointment_requires_authentication(self):
        target_date = timezone.localdate() + timedelta(days=1)
        url = reverse("business-appointment-create", args=[self.business.slug])
        payload = {
            "service_id": str(self.service.id),
            "date": target_date.isoformat(),
            "start_time": "10:00",
        }
        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_appointment_success(self):
        target_date = timezone.localdate() + timedelta(days=1)
        url = reverse("business-appointment-create", args=[self.business.slug])
        payload = {
            "service_id": str(self.service.id),
            "date": target_date.isoformat(),
            "start_time": "11:00",
            "notes": "Proszę o strzyzenie klasyczne.",
        }

        self.client.force_authenticate(self.user)
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Appointment.objects.count(), 1)

        appointment = Appointment.objects.first()
        self.assertIsNotNone(appointment)
        self.assertEqual(appointment.service, self.service)
        self.assertEqual(appointment.customer, self.user)

    def test_create_appointment_duplicate_slot(self):
        target_date = timezone.localdate() + timedelta(days=1)
        start_time = "12:00"

        self.client.force_authenticate(self.user)
        url = reverse("business-appointment-create", args=[self.business.slug])
        payload = {
            "service_id": str(self.service.id),
            "date": target_date.isoformat(),
            "start_time": start_time,
        }

        # First booking succeeds
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Second booking should fail for the same slot
        other_user = User.objects.create_user(username="anna", email="anna@example.com", password="secret123")
        self.client.force_authenticate(other_user)
        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
