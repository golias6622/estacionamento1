from math import ceil

from django.utils import timezone
from rest_framework import serializers

from users.models import (
    Customer,
    ParkingSession,
    ParkingSpot,
    UserProfileExample,
    Vehicle,
)


class UserProfileExampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfileExample
        fields = ["id", "address", "phone_number", "birth_date", "user"]


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id", "name", "phone_number", "email"]


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ["id", "customer", "plate", "make", "model", "color"]

    def validate_plate(self, value):
        return value.strip().upper()


class ParkingSpotSerializer(serializers.ModelSerializer):
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = ParkingSpot
        fields = ["id", "number", "is_available"]


class ParkingSessionSerializer(serializers.ModelSerializer):
    duration_minutes = serializers.SerializerMethodField()
    vehicle_plate = serializers.CharField(source="vehicle.plate", read_only=True)
    spot_number = serializers.IntegerField(source="spot.number", read_only=True)

    class Meta:
        model = ParkingSession
        fields = [
            "id",
            "vehicle",
            "vehicle_plate",
            "spot",
            "spot_number",
            "entry_at",
            "exit_at",
            "duration_minutes",
            "hourly_rate",
            "amount_charged",
        ]
        read_only_fields = [
            "spot",
            "entry_at",
            "exit_at",
            "duration_minutes",
            "hourly_rate",
            "amount_charged",
        ]

    def get_duration_minutes(self, session):
        end = session.exit_at or timezone.now()
        return max(0, ceil((end - session.entry_at).total_seconds() / 60))

    def validate_vehicle(self, vehicle):
        if ParkingSession.objects.filter(
            vehicle=vehicle, exit_at__isnull=True
        ).exists():
            raise serializers.ValidationError(
                "Este veículo já possui uma entrada sem saída registrada."
            )
        return vehicle
