from django.db.models import Count, Prefetch, Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Business, BusinessService
from .serializers import (
    AppointmentCreateSerializer,
    BusinessAvailabilitySerializer,
    BusinessDetailSerializer,
    BusinessListSerializer,
)


class BusinessCategoryListView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        counts = (
            Business.objects.values("category")
            .annotate(total=Count("id"))
            .order_by()
        )
        count_map = {entry["category"]: entry["total"] for entry in counts}

        data = [
            {"slug": value, "name": label, "count": count_map.get(value, 0)}
            for value, label in Business.Category.choices
        ]
        return Response(data, status=status.HTTP_200_OK)


class BusinessListView(generics.ListAPIView):
    serializer_class = BusinessListSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        queryset = Business.objects.prefetch_related(
            Prefetch("services", queryset=BusinessService.objects.filter(is_active=True))
        )
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(category=category)

        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(city__icontains=search))

        return queryset


class BusinessDetailView(generics.RetrieveAPIView):
    queryset = Business.objects.prefetch_related(
        Prefetch("services", queryset=BusinessService.objects.filter(is_active=True)),
        "opening_hours",
    )
    serializer_class = BusinessDetailSerializer
    lookup_field = "slug"
    permission_classes = (AllowAny,)


class BusinessAvailabilityView(APIView):
    permission_classes = (AllowAny,)

    def get_business(self, slug: str) -> Business:
        return get_object_or_404(
            Business.objects.prefetch_related(
                Prefetch("services", queryset=BusinessService.objects.filter(is_active=True)),
                "opening_hours",
            ),
            slug=slug,
        )

    def get(self, request, slug: str):
        business = self.get_business(slug)
        serializer = BusinessAvailabilitySerializer(
            data=request.query_params,
            context={"business": business},
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.to_representation(
            {"service": serializer.validated_data["service"], "date": serializer.validated_data["date"]}
        )
        return Response(data, status=status.HTTP_200_OK)


class BusinessAppointmentCreateView(generics.CreateAPIView):
    serializer_class = AppointmentCreateSerializer
    permission_classes = (IsAuthenticated,)

    def get_business(self) -> Business:
        if not hasattr(self, "_business"):
            self._business = get_object_or_404(
                Business.objects.prefetch_related(
                    Prefetch("services", queryset=BusinessService.objects.filter(is_active=True)),
                    "opening_hours",
                ),
                slug=self.kwargs["slug"],
            )
        return self._business

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["business"] = self.get_business()
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.to_representation(appointment), status=status.HTTP_201_CREATED, headers=headers)
