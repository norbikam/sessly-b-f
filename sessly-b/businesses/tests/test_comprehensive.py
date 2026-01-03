"""
Additional comprehensive tests for businesses app.
"""

from datetime import time, timedelta
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from businesses.models import Appointment, Business, BusinessOpeningHour, BusinessService

User = get_user_model()


class CustomerAppointmentTests(APITestCase):
    """Tests for customer appointment management."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="customer",
            email="customer@example.com",
            password="Test123!@#",
            is_active=True
        )
        
        self.business = Business.objects.create(
            name="Test Salon",
            slug="test-salon",
            category=Business.Category.HAIRDRESSER,
            timezone="Europe/Warsaw",
            address_line1="Test Street 1",
            city="Warsaw",
            postal_code="00-001",
            country="Poland",
        )
        
        self.service = BusinessService.objects.create(
            business=self.business,
            name="Haircut",
            duration_minutes=60,
            buffer_minutes=0,
            price_amount=100,
            price_currency="PLN",
        )
        
        # Create appointment
        tomorrow = timezone.now() + timedelta(days=1)
        self.appointment = Appointment.objects.create(
            business=self.business,
            service=self.service,
            customer=self.user,
            start=tomorrow,
            end=tomorrow + timedelta(minutes=60),
            status=Appointment.Status.PENDING
        )
        
        self.client.force_authenticate(self.user)
    
    def test_list_my_appointments(self):
        """Test listing user's appointments."""
        url = reverse('customer-appointments-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_filter_appointments_by_status(self):
        """Test filtering appointments by status."""
        url = reverse('customer-appointments-list')
        response = self.client.get(url, {'status': 'pending'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_cancel_appointment(self):
        """Test cancelling an appointment."""
        url = reverse('customer-appointments-cancel', args=[self.appointment.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify appointment was cancelled
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, Appointment.Status.CANCELLED)
    
    def test_cannot_cancel_past_appointment(self):
        """Test that past appointments cannot be cancelled."""
        # Create past appointment
        yesterday = timezone.now() - timedelta(days=1)
        past_appointment = Appointment.objects.create(
            business=self.business,
            service=self.service,
            customer=self.user,
            start=yesterday,
            end=yesterday + timedelta(minutes=60),
            status=Appointment.Status.CONFIRMED
        )
        
        url = reverse('customer-appointments-cancel', args=[past_appointment.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class BusinessOwnerTests(APITestCase):
    """Tests for business owner management."""
    
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="Test123!@#",
            is_active=True,
            role=User.Role.BUSINESS_OWNER
        )
        
        self.business = Business.objects.create(
            name="My Salon",
            slug="my-salon",
            category=Business.Category.HAIRDRESSER,
            owner=self.owner,
            timezone="Europe/Warsaw",
            address_line1="Owner Street 1",
            city="Warsaw",
            postal_code="00-001",
            country="Poland",
        )
        
        self.client.force_authenticate(self.owner)
    
    def test_list_my_businesses(self):
        """Test listing owner's businesses."""
        url = reverse('my-business-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_service(self):
        """Test creating a service."""
        url = reverse('business-services-list', args=[self.business.slug])
        data = {
            'name': 'New Service',
            'description': 'Test description',
            'duration_minutes': 30,
            'buffer_minutes': 10,
            'price_amount': 50,
            'price_currency': 'PLN',
            'is_active': True
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BusinessService.objects.count(), 1)
    
    def test_update_service(self):
        """Test updating a service."""
        service = BusinessService.objects.create(
            business=self.business,
            name="Old Service",
            duration_minutes=60,
            price_amount=100,
            price_currency="PLN"
        )
        
        url = reverse('business-services-detail', args=[self.business.slug, service.id])
        data = {
            'name': 'Updated Service',
            'duration_minutes': 45,
            'price_amount': 80,
            'price_currency': 'PLN',
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        service.refresh_from_db()
        self.assertEqual(service.name, 'Updated Service')
    
    def test_create_opening_hours(self):
        """Test creating opening hours."""
        url = reverse('business-opening-hours-list', args=[self.business.slug])
        data = {
            'day_of_week': 0,  # Monday
            'is_closed': False,
            'open_time': '09:00',
            'close_time': '17:00'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BusinessOpeningHour.objects.count(), 1)
    
    def test_bulk_update_opening_hours(self):
        """Test bulk updating opening hours."""
        url = reverse('business-opening-hours-bulk-update', args=[self.business.slug])
        data = [
            {'day_of_week': i, 'is_closed': False, 'open_time': '09:00', 'close_time': '17:00'}
            for i in range(7)
        ]
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(BusinessOpeningHour.objects.count(), 7)
    
    def test_business_stats(self):
        """Test getting business statistics."""
        url = reverse('my-business-stats', args=[self.business.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total', response.data['data'])
        self.assertIn('upcoming', response.data['data'])


class AppointmentConfirmationTests(APITestCase):
    """Tests for appointment confirmation by business owner."""
    
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="Test123!@#",
            role=User.Role.BUSINESS_OWNER
        )
        
        self.customer = User.objects.create_user(
            username="customer",
            email="customer@example.com",
            password="Test123!@#"
        )
        
        self.business = Business.objects.create(
            name="Test Business",
            slug="test-business",
            category=Business.Category.HAIRDRESSER,
            owner=self.owner,
            timezone="Europe/Warsaw",
            address_line1="Test St",
            city="Warsaw",
            postal_code="00-001",
            country="Poland",
        )
        
        self.service = BusinessService.objects.create(
            business=self.business,
            name="Service",
            duration_minutes=60,
            price_amount=100,
            price_currency="PLN",
        )
        
        tomorrow = timezone.now() + timedelta(days=1)
        self.appointment = Appointment.objects.create(
            business=self.business,
            service=self.service,
            customer=self.customer,
            start=tomorrow,
            end=tomorrow + timedelta(minutes=60),
            status=Appointment.Status.PENDING
        )
        
        self.client.force_authenticate(self.owner)
    
    def test_confirm_appointment(self):
        """Test confirming an appointment."""
        url = reverse('business-appointments-confirm', args=[self.business.slug, self.appointment.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, Appointment.Status.CONFIRMED)
        self.assertIsNotNone(self.appointment.confirmed_at)
    
    def test_cancel_appointment_by_owner(self):
        """Test cancelling an appointment by owner."""
        url = reverse('business-appointments-cancel', args=[self.business.slug, self.appointment.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, Appointment.Status.CANCELLED)
