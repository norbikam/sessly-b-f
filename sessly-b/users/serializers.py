from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers

from .models import EmailVerification
from .services import create_email_verification, send_verification_email

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, style={"input_type": "password"})
    password2 = serializers.CharField(write_only=True, required=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password", "password2")

    def validate_email(self, value: str) -> str:
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Uzytkownik z takim adresem email juz istnieje")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Hasla nie sa identyczne"})

        temp_user = User(
            username=attrs.get("username"),
            email=attrs.get("email"),
            first_name=attrs.get("first_name"),
            last_name=attrs.get("last_name"),
        )
        validate_password(attrs["password"], user=temp_user)
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")

        with transaction.atomic():
            user = User.objects.create_user(password=password, **validated_data)
            verification_enabled = getattr(settings, "EMAIL_VERIFICATION_ENABLED", True)

            if verification_enabled:
                if user.is_active:
                    user.is_active = False
                    user.save(update_fields=["is_active"])

                _, code = create_email_verification(user)
                send_verification_email(user, code)
            elif not user.is_active:
                user.is_active = True
                user.save(update_fields=["is_active"])

        return user


class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(min_length=6, max_length=6)

    default_error_messages = {
        "invalid_code": "Niepoprawny kod potwierdzenia",
        "already_confirmed": "Adres email zostal juz potwierdzony",
        "code_expired": "Kod potwierdzenia wygasl. Popros o nowy kod.",
    }

    def validate(self, attrs):
        email = attrs["email"]
        code = attrs["code"]

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist as exc:  # pragma: no cover - security measure
            raise serializers.ValidationError({"email": "Nie znaleziono uzytkownika z tym adresem"}) from exc

        if user.is_active:
            self.fail("already_confirmed")

        verification = (
            EmailVerification.objects.filter(user=user, code=code)
            .order_by("-created_at")
            .select_related("user")
            .first()
        )
        if not verification:
            self.fail("invalid_code")

        if verification.has_expired():
            self.fail("code_expired")

        if verification.is_used:
            self.fail("invalid_code")

        attrs["user"] = user
        attrs["verification"] = verification
        return attrs

    def save(self, **kwargs):
        verification: EmailVerification = self.validated_data["verification"]
        user = self.validated_data["user"]

        user.is_active = True
        user.save(update_fields=["is_active"])
        verification.mark_used()
        return user


class ResendVerificationEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    default_error_messages = {
        "not_found": "Nie znaleziono uzytkownika z tym adresem",
        "already_confirmed": "Adres email zostal juz potwierdzony",
    }

    def validate_email(self, value):
        try:
            user = User.objects.get(email__iexact=value)
        except User.DoesNotExist as exc:  # pragma: no cover - security measure
            raise serializers.ValidationError(self.error_messages["not_found"]) from exc

        if user.is_active:
            raise serializers.ValidationError(self.error_messages["already_confirmed"])

        self.context["user"] = user
        return value

    def save(self, **kwargs):
        user = self.context["user"]
        _, code = create_email_verification(user)
        send_verification_email(user, code)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name")


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True, style={"input_type": "password"})
    new_password = serializers.CharField(required=True, write_only=True, style={"input_type": "password"})
    new_password2 = serializers.CharField(required=True, write_only=True, style={"input_type": "password"})

    def validate_old_password(self, value):
        user = self.context.get("request").user if self.context.get("request") else None
        if not user or not user.check_password(value):
            raise serializers.ValidationError("Niepoprawne haslo")
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password2"]:
            raise serializers.ValidationError({"new_password": "Hasla nie sa identyczne"})

        user = self.context.get("request").user if self.context.get("request") else None
        validate_password(attrs["new_password"], user=user)
        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        new_password = self.validated_data["new_password"]
        user.set_password(new_password)
        user.save()
        return user
