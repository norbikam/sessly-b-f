from django.contrib import admin

from .models import EmailVerification


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ("user", "code", "created_at", "expires_at", "used_at")
    search_fields = ("user__username", "user__email", "code")
    list_filter = ("used_at", "expires_at")
    autocomplete_fields = ("user",)
