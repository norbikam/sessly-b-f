"""
Views for customer-facing appointment management.
"""

import logging
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.exceptions import ErrorCode
from backend.logging_config import log_appointment_action
from backend.responses import error_response, success_response
from .models import Appointment
from .serializers import AppointmentSerializer

logger = logging.getLogger(__name__)


class CustomerAppointmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for customers to manage their own appointments.
    
    Endpoints:
    - GET /api/appointments/ - List all user's appointments
    - GET /api/appointments/{id}/ - Get appointment detail
    - POST /api/appointments/{id}/cancel/ - Cancel appointment
    - POST /api/appointments/{id}/reschedule/ - Reschedule appointment (TODO)
    """
    
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get appointments for the current user."""
        user = self.request.user
        queryset = Appointment.objects.filter(customer=user).select_related(
            'business', 'service', 'staff'
        ).order_by('-start')
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by time (upcoming, past)
        time_filter = self.request.query_params.get('time')
        now = timezone.now()
        
        if time_filter == 'upcoming':
            queryset = queryset.filter(start__gte=now)
        elif time_filter == 'past':
            queryset = queryset.filter(start__lt=now)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel an appointment.
        
        Only upcoming appointments can be cancelled.
        """
        appointment = self.get_object()
        
        # Check if appointment is already cancelled
        if appointment.status == Appointment.Status.CANCELLED:
            return error_response(
                error_code=ErrorCode.BAD_REQUEST,
                message="Ta rezerwacja została już anulowana",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if appointment is in the past
        if appointment.start < timezone.now():
            return error_response(
                error_code=ErrorCode.BAD_REQUEST,
                message="Nie można anulować rezerwacji z przeszłości",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Cancel the appointment
        appointment.status = Appointment.Status.CANCELLED
        appointment.save(update_fields=['status', 'updated_at'])
        
        # Log the cancellation
        log_appointment_action(
            logger, 
            appointment, 
            "cancelled", 
            user=request.user,
            details=f"Business: {appointment.business.name}"
        )
        
        serializer = self.get_serializer(appointment)
        return success_response(
            data=serializer.data,
            message="Rezerwacja została anulowana",
            status_code=status.HTTP_200_OK
        )
