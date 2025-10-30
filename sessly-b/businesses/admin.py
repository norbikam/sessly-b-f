from django.contrib import admin

from .models import Appointment, Business, BusinessOpeningHour, BusinessService


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "city", "phone_number")
    search_fields = ("name", "city", "postal_code")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(BusinessOpeningHour)
class BusinessOpeningHourAdmin(admin.ModelAdmin):
    list_display = ("business", "day_of_week", "is_closed", "open_time", "close_time")
    list_filter = ("business", "day_of_week", "is_closed")


@admin.register(BusinessService)
class BusinessServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "business", "duration_minutes", "price_amount", "is_active")
    list_filter = ("business", "is_active")
    search_fields = ("name",)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("service", "business", "customer", "start", "status")
    list_filter = ("business", "status")
    search_fields = ("customer__username", "customer__email", "service__name")
    autocomplete_fields = ("business", "service", "customer")
