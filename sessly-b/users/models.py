from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)
    business = models.OneToOneField(
        "businesses.Business",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owner",
    )

    class Role(models.TextChoices):
        CUSTOMER = "customer", "Klient"
        BUSINESS_OWNER = "business_owner", "Właściciel firmy"
        ADMIN = "admin", "Admin"
        STAFF = "staff", "Pracownik"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
    )

    favorite_businesses = models.ManyToManyField(
        "businesses.Business", related_name="favorited_by", blank=True
    )


class EmailVerification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="email_verifications",
    )
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["user", "code"])]
        ordering = ("-created_at",)

    @property
    def is_used(self) -> bool:
        return self.used_at is not None

    def mark_used(self) -> None:
        if not self.used_at:
            self.used_at = timezone.now()
            self.save(update_fields=["used_at"])

    def has_expired(self) -> bool:
        return timezone.now() >= self.expires_at

    def is_valid(self) -> bool:
        return not self.is_used and not self.has_expired()

    def __str__(self) -> str:
        return f"{self.user} - {self.code}"