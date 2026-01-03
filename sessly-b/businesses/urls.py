from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    BusinessAppointmentCreateView,
    BusinessAvailabilityView,
    BusinessCategoryListView,
    BusinessDetailView,
    BusinessListView,
    BusinessStaffViewSet,
    BusinessAppointmentViewSet,
)
from .customer_views import CustomerAppointmentViewSet
from .owner_views import (
    BusinessManagementViewSet,
    BusinessServiceViewSet,
    BusinessOpeningHoursViewSet,
)

router = DefaultRouter()

# Business owner routes
router.register(r'my-business', BusinessManagementViewSet, basename='my-business')

# Business staff management
router.register(
    r"(?P<slug>[-\w]+)/staff", BusinessStaffViewSet, basename="business-staff"
)

# Business services management (owner)
router.register(
    r"(?P<slug>[-\w]+)/services", BusinessServiceViewSet, basename="business-services"
)

# Business opening hours management (owner)
router.register(
    r"(?P<slug>[-\w]+)/opening-hours", BusinessOpeningHoursViewSet, basename="business-opening-hours"
)

# Business appointments management (owner)
router.register(
    r"(?P<slug>[-\w]+)/appointments",
    BusinessAppointmentViewSet,
    basename="business-appointments",
)

urlpatterns = [
    path("categories/", BusinessCategoryListView.as_view(), name="business-category-list"),
    path("", BusinessListView.as_view(), name="business-list"),
    path("<slug:slug>/", BusinessDetailView.as_view(), name="business-detail"),
    path("<slug:slug>/availability/", BusinessAvailabilityView.as_view(), name="business-availability"),
    path("<slug:slug>/appointments/", BusinessAppointmentCreateView.as_view(), name="business-appointment-create"),
    path("", include(router.urls)),
]
