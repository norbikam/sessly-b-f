from __future__ import annotations

from datetime import datetime

from django.utils import timezone
from rest_framework import serializers

from .models import (
    Appointment,
    Business,
    BusinessOpeningHour,
    BusinessService,
    BusinessStaff,
)
from .services import (
    SlotUnavailableError,
    calculate_daily_availability,
    create_appointment,
    get_business_timezone,
    is_slot_available,
    serialize_time_list,
)


class BusinessOpeningHourSerializer(serializers.ModelSerializer):
    day_name = serializers.CharField(source="get_day_of_week_display", read_only=True)

    class Meta:
        model = BusinessOpeningHour
        fields = ("day_of_week", "day_name", "is_closed", "open_time", "close_time")


class BusinessServiceSerializer(serializers.ModelSerializer):
    total_slot_minutes = serializers.IntegerField(read_only=True)

    class Meta:
        model = BusinessService
        fields = (
            "id",
            "name",
            "description",
            "duration_minutes",
            "buffer_minutes",
            "total_slot_minutes",
            "price_amount",
            "price_currency",
            "is_active",
            "color",
        )


class BusinessListSerializer(serializers.ModelSerializer):
    services_count = serializers.SerializerMethodField()

    class Meta:
        model = Business
        fields = (
            "id",
            "name",
            "slug",
            "category",
            "description",
            "city",
            "address_line1",
            "address_line2",
            "postal_code",
            "country",
            "phone_number",
            "website_url",
            "services_count",
        )

    def get_services_count(self, obj) -> int:
        services = getattr(obj, "services", None)
        if services is None:
            return obj.services.filter(is_active=True).count()
        return sum(1 for service in services.all() if service.is_active)


class BusinessStaffSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(write_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = BusinessStaff
        fields = (
            "id",
            "user_id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_manager",
        )
        read_only_fields = ("id", "username", "first_name", "last_name", "email")


class BusinessDetailSerializer(BusinessListSerializer):
    opening_hours = BusinessOpeningHourSerializer(many=True, read_only=True)
    services = BusinessServiceSerializer(many=True, read_only=True)

    class Meta(BusinessListSerializer.Meta):
        fields = BusinessListSerializer.Meta.fields + (
            "email",
            "timezone",
            "latitude",
            "longitude",
            "opening_hours",
            "services",
        )


class BusinessCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating businesses."""
    
    class Meta:
        model = Business
        fields = (
            "id",
            "name",
            "slug",
            "category",
            "description",
            "email",
            "phone_number",
            "website_url",
            "address_line1",
            "address_line2",
            "city",
            "postal_code",
            "country",
            "timezone",
            "latitude",
            "longitude",
        )
        read_only_fields = ("id",)
    
    def validate_slug(self, value):
        """Ensure slug is unique (except for current instance on update)."""
        queryset = Business.objects.filter(slug=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("Biznes z tym slug już istnieje")
        return value


class BusinessAvailabilitySerializer(serializers.Serializer):
    date = serializers.DateField()
    service_id = serializers.UUIDField()

    def validate(self, attrs):
        business: Business = self.context["business"]
        try:
            service = business.services.get(id=attrs["service_id"], is_active=True)
        except BusinessService.DoesNotExist as exc:
            raise serializers.ValidationError(
                {"service_id": "Nie znaleziono uslugi"}
            ) from exc

        attrs["service"] = service
        return attrs

    def to_representation(self, instance):
        business: Business = self.context["business"]
        service: BusinessService = instance["service"]
        target_date = instance["date"]

        availability = calculate_daily_availability(business, service, target_date)
        return {
            "date": target_date,
            "service_id": str(service.id),
            "slots": serialize_time_list(availability),
        }


class AppointmentSerializer(serializers.ModelSerializer):
    service = BusinessServiceSerializer(read_only=True)
    business = serializers.SlugRelatedField(slug_field="slug", read_only=True)

    class Meta:
        model = Appointment
        fields = (
            "id",
            "business",
            "service",
            "status",
            "start",
            "end",
            "notes",
            "google_event_id",
            "created_at",
        )
        read_only_fields = fields


class AppointmentCreateSerializer(serializers.Serializer):
    service_id = serializers.UUIDField()
    date = serializers.DateField()
    start_time = serializers.TimeField()
    notes = serializers.CharField(max_length=500, allow_blank=True, required=False)

    default_error_messages = {
        "past_slot": "Nie mozna zarezerwowac terminu w przeszlosci.",
        "slot_unavailable": "Wybrany termin nie jest juz dostepny.",
    }

    def validate(self, attrs):
        business: Business = self.context["business"]
        request = self.context["request"]
        try:
            service = business.services.get(id=attrs["service_id"], is_active=True)
        except BusinessService.DoesNotExist as exc:
            raise serializers.ValidationError(
                {"service_id": "Nie znaleziono uslugi"}
            ) from exc

        tz = get_business_timezone(business)
        start_local = datetime.combine(attrs["date"], attrs["start_time"], tzinfo=tz)
        now_local = timezone.now().astimezone(tz)
        if start_local < now_local:
            self.fail("past_slot")

        if not is_slot_available(business, service, start_local):
            self.fail("slot_unavailable")

        attrs["service"] = service
        attrs["start_local"] = start_local
        attrs["customer"] = request.user
        attrs["notes"] = attrs.get("notes", "").strip()
        return attrs

    def create(self, validated_data):
        business: Business = self.context["business"]
        try:
            appointment = create_appointment(
                business=business,
                service=validated_data["service"],
                customer=validated_data["customer"],
                start_local=validated_data["start_local"],
                notes=validated_data["notes"],
            )
        except SlotUnavailableError:
            self.fail("slot_unavailable")

        return appointment

    def to_representation(self, instance):
        return AppointmentSerializer(instance).data


class AdminAppointmentSerializer(serializers.ModelSerializer):
    service = BusinessServiceSerializer(read_only=True)
    business = serializers.SlugRelatedField(slug_field="slug", read_only=True)
    customer_email = serializers.EmailField(source="customer.email", read_only=True)
    customer_first_name = serializers.CharField(
        source="customer.first_name", read_only=True
    )
    customer_last_name = serializers.CharField(
        source="customer.last_name", read_only=True
    )

    class Meta:
        model = Appointment
        fields = (
            "id",
            "business",
            "service",
            "customer_email",
            "customer_first_name",
            "customer_last_name",
            "staff",
            "status",
            "start",
            "end",
            "notes",
            "google_event_id",
            "created_at",
            "updated_at",
            "confirmed_at",
        )
        read_only_fields = fields


class OwnerAppointmentSerializer(serializers.Serializer):
    service = BusinessServiceSerializer(read_only=True)
    business = serializers.SlugRelatedField(slug_field="slug", read_only=True)
    customer_email = serializers.EmailField(source="customer.email", read_only=True)
    staff = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Appointment
        fields = (
            "id",
            "business",
            "service",
            "customer_email",
            "staff",
            "status",
            "start",
            "end",
            "notes",
            "google_event_id",
            "created_at",
            "updated_at",
            "confirmed_at",
        )
        read_only_fields = fields
