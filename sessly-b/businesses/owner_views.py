"""
Views for business owners to manage their businesses.
"""

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.exceptions import ErrorCode
from backend.responses import error_response, success_response
from users.permissions import IsBusinessOwner
from .models import Business, BusinessOpeningHour, BusinessService
from .serializers import (
    BusinessCreateUpdateSerializer,
    BusinessDetailSerializer,
    BusinessOpeningHourSerializer,
    BusinessServiceSerializer,
)


class BusinessManagementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for business owners to manage their business details.
    
    Endpoints:
    - GET /api/my-business/ - Get business details
    - POST /api/my-business/ - Create business
    - PUT /api/my-business/{id}/ - Update business
    - PATCH /api/my-business/{id}/ - Partial update
    - DELETE /api/my-business/{id}/ - Delete business
    """
    
    permission_classes = [IsAuthenticated, IsBusinessOwner]
    
    def get_queryset(self):
        """Get businesses owned by the current user."""
        return Business.objects.filter(owner=self.request.user).prefetch_related(
            'services', 'opening_hours', 'staff_members'
        )
    
    def get_serializer_class(self):
        """Use different serializer for list/retrieve vs create/update."""
        if self.action in ['list', 'retrieve']:
            return BusinessDetailSerializer
        return BusinessCreateUpdateSerializer
    
    def perform_create(self, serializer):
        """Set the owner when creating a business."""
        serializer.save(owner=self.request.user)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """
        Get business statistics.
        
        Returns:
        - Total appointments
        - Upcoming appointments
        - Completed appointments
        - Cancelled appointments
        - Revenue (if price data available)
        """
        business = self.get_object()
        
        from django.db.models import Count, Q
        from datetime import datetime, timedelta
        from django.utils import timezone
        
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)
        
        stats = business.appointments.aggregate(
            total=Count('id'),
            upcoming=Count('id', filter=Q(start__gte=now, status='pending')),
            confirmed=Count('id', filter=Q(status='confirmed')),
            completed=Count('id', filter=Q(start__lt=now, status='confirmed')),
            cancelled=Count('id', filter=Q(status='cancelled')),
            last_30_days=Count('id', filter=Q(created_at__gte=thirty_days_ago)),
        )
        
        return success_response(data=stats)


class BusinessServiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for business owners to manage their services.
    
    Endpoints:
    - GET /api/businesses/{slug}/services/ - List services
    - POST /api/businesses/{slug}/services/ - Create service
    - PUT /api/businesses/{slug}/services/{id}/ - Update service
    - PATCH /api/businesses/{slug}/services/{id}/ - Partial update
    - DELETE /api/businesses/{slug}/services/{id}/ - Delete service
    """
    
    serializer_class = BusinessServiceSerializer
    permission_classes = [IsAuthenticated, IsBusinessOwner]
    
    def get_queryset(self):
        """Get services for the business."""
        slug = self.kwargs.get('slug')
        business = get_object_or_404(Business, slug=slug, owner=self.request.user)
        return BusinessService.objects.filter(business=business)
    
    def get_business(self):
        """Get the business from the URL."""
        slug = self.kwargs.get('slug')
        return get_object_or_404(Business, slug=slug, owner=self.request.user)
    
    def perform_create(self, serializer):
        """Set the business when creating a service."""
        business = self.get_business()
        serializer.save(business=business)
    
    def perform_update(self, serializer):
        """Ensure business is set correctly on update."""
        business = self.get_business()
        serializer.save(business=business)


class BusinessOpeningHoursViewSet(viewsets.ModelViewSet):
    """
    ViewSet for business owners to manage opening hours.
    
    Endpoints:
    - GET /api/businesses/{slug}/opening-hours/ - List opening hours
    - POST /api/businesses/{slug}/opening-hours/ - Create opening hours
    - PUT /api/businesses/{slug}/opening-hours/{id}/ - Update hours
    - PATCH /api/businesses/{slug}/opening-hours/{id}/ - Partial update
    - DELETE /api/businesses/{slug}/opening-hours/{id}/ - Delete hours
    """
    
    serializer_class = BusinessOpeningHourSerializer
    permission_classes = [IsAuthenticated, IsBusinessOwner]
    
    def get_queryset(self):
        """Get opening hours for the business."""
        slug = self.kwargs.get('slug')
        business = get_object_or_404(Business, slug=slug, owner=self.request.user)
        return BusinessOpeningHour.objects.filter(business=business).order_by('day_of_week')
    
    def get_business(self):
        """Get the business from the URL."""
        slug = self.kwargs.get('slug')
        return get_object_or_404(Business, slug=slug, owner=self.request.user)
    
    def perform_create(self, serializer):
        """Set the business when creating opening hours."""
        business = self.get_business()
        serializer.save(business=business)
    
    def perform_update(self, serializer):
        """Ensure business is set correctly on update."""
        business = self.get_business()
        serializer.save(business=business)
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request, slug=None):
        """
        Bulk update all opening hours for the week.
        
        Expects a list of opening hours objects:
        [
            {"day_of_week": 0, "is_closed": false, "open_time": "09:00", "close_time": "17:00"},
            {"day_of_week": 1, "is_closed": false, "open_time": "09:00", "close_time": "17:00"},
            ...
        ]
        """
        business = self.get_business()
        hours_data = request.data
        
        if not isinstance(hours_data, list):
            return error_response(
                error_code=ErrorCode.VALIDATION_ERROR,
                message="Dane muszą być listą godzin otwarcia",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            # Delete existing hours
            BusinessOpeningHour.objects.filter(business=business).delete()
            
            # Create new hours
            created_hours = []
            for hour_data in hours_data:
                serializer = self.get_serializer(data=hour_data)
                serializer.is_valid(raise_exception=True)
                hour = serializer.save(business=business)
                created_hours.append(hour)
        
        serializer = self.get_serializer(created_hours, many=True)
        return success_response(
            data=serializer.data,
            message="Godziny otwarcia zostały zaktualizowane",
            status_code=status.HTTP_200_OK
        )
