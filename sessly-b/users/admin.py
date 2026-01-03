from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import EmailVerification, User


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ("user", "code", "created_at", "expires_at", "used_at")
    search_fields = ("user__username", "user__email", "code")
    list_filter = ("used_at", "expires_at")
    autocomplete_fields = ("user",)

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    pass