from django.urls import path

from .views import (
    BusinessAppointmentCreateView,
    BusinessAvailabilityView,
    BusinessCategoryListView,
    BusinessDetailView,
    BusinessListView,
)

urlpatterns = [
    path("categories/", BusinessCategoryListView.as_view(), name="business-category-list"),
    path("", BusinessListView.as_view(), name="business-list"),
    path("<slug:slug>/", BusinessDetailView.as_view(), name="business-detail"),
    path("<slug:slug>/availability/", BusinessAvailabilityView.as_view(), name="business-availability"),
    path("<slug:slug>/appointments/", BusinessAppointmentCreateView.as_view(), name="business-appointment-create"),
]
