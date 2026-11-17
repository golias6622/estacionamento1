from math import ceil

from django.conf import settings
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from rest_framework import serializers
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from users.api.serializers import (
    CustomerSerializer,
    ParkingSessionSerializer,
    ParkingSpotSerializer,
    UserProfileExampleSerializer,
    VehicleSerializer,
)

from users.models import (
    Customer,
    ParkingSession,
    ParkingSpot,
    UserProfileExample,
    Vehicle,
)

class UserProfileExampleViewSet(ModelViewSet):
    serializer_class = UserProfileExampleSerializer
    permission_classes = [AllowAny]
    queryset = UserProfileExample.objects.all()
    http_method_names = ['get', 'put']


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [AllowAny]


class VehicleViewSet(ModelViewSet):
    queryset = Vehicle.objects.select_related("customer").all()
    serializer_class = VehicleSerializer
    permission_classes = [AllowAny]


class ParkingSpotViewSet(ModelViewSet):
    queryset = ParkingSpot.objects.all()
    serializer_class = ParkingSpotSerializer
    permission_classes = [AllowAny]


class ParkingSessionViewSet(ModelViewSet):
    queryset = ParkingSession.objects.select_related("vehicle", "spot").all()
    serializer_class = ParkingSessionSerializer
    permission_classes = [AllowAny]
    http_method_names = ["get", "post", "head", "options"]

    @transaction.atomic
    def perform_create(self, serializer):
        available_spot = None
        for spot in ParkingSpot.objects.select_for_update().order_by("number"):
            if spot.is_available:
                available_spot = spot
                break

        if available_spot is None:
            raise serializers.ValidationError(
                {"detail": "Não há vagas disponíveis no momento."}
            )

        serializer.save(
            spot=available_spot,
            hourly_rate=settings.PARKING_HOURLY_RATE,
        )

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def checkout(self, request, pk=None):
        parking_session = self.get_object()
        if parking_session.exit_at is not None:
            raise serializers.ValidationError(
                {"detail": "A saída deste veículo já foi registrada."}
            )

        exit_at = timezone.now()
        elapsed_seconds = max(
            0, (exit_at - parking_session.entry_at).total_seconds()
        )
        charged_hours = max(1, ceil(elapsed_seconds / 3600))
        parking_session.exit_at = exit_at
        parking_session.amount_charged = (
            parking_session.hourly_rate * charged_hours
        )
        parking_session.save(update_fields=["exit_at", "amount_charged"])
        return Response(self.get_serializer(parking_session).data)


@api_view(["GET"])
def parking_summary(request):
    spots = list(ParkingSpot.objects.all())
    available_spots = sum(spot.is_available for spot in spots)
    active_sessions = ParkingSession.objects.filter(exit_at__isnull=True)
    total_revenue = ParkingSession.objects.aggregate(
        total=Sum("amount_charged")
    )["total"]

    return Response(
        {
            "total_customers": Customer.objects.count(),
            "total_vehicles": Vehicle.objects.count(),
            "total_spots": len(spots),
            "available_spots": available_spots,
            "occupied_spots": len(spots) - available_spots,
            "vehicles_parked": active_sessions.count(),
            "total_revenue": total_revenue or 0,
        }
    )
