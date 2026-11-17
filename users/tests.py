from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from users.models import Customer, ParkingSession, ParkingSpot, Vehicle

# Create your tests here.


class ParkingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer = Customer.objects.create(name="Maria Silva")
        self.vehicle = Vehicle.objects.create(
            customer=self.customer, plate="ABC1D23", model="Argo"
        )
        self.spot = ParkingSpot.objects.create(number=1)

    def test_entry_checkout_and_summary(self):
        entry_response = self.client.post(
            "/api/parking-sessions/",
            {"vehicle": self.vehicle.id},
            format="json",
        )
        self.assertEqual(entry_response.status_code, status.HTTP_201_CREATED)
        session = ParkingSession.objects.get(id=entry_response.data["id"])
        ParkingSession.objects.filter(id=session.id).update(
            entry_at=timezone.now() - timedelta(minutes=61)
        )

        checkout_response = self.client.post(
            f"/api/parking-sessions/{session.id}/checkout/",
            format="json",
        )
        self.assertEqual(checkout_response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(checkout_response.data["duration_minutes"], 61)
        self.assertLessEqual(checkout_response.data["duration_minutes"], 62)
        self.assertEqual(checkout_response.data["amount_charged"], "20.00")

        summary_response = self.client.get("/api/summary/")
        self.assertEqual(summary_response.data["available_spots"], 1)
        self.assertEqual(summary_response.data["vehicles_parked"], 0)
        self.assertEqual(summary_response.data["total_revenue"], Decimal("20.00"))

    def test_vehicle_cannot_enter_twice_without_checkout(self):
        self.client.post(
            "/api/parking-sessions/",
            {"vehicle": self.vehicle.id},
            format="json",
        )

        response = self.client.post(
            "/api/parking-sessions/",
            {"vehicle": self.vehicle.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_entry_is_rejected_when_there_are_no_available_spots(self):
        ParkingSession.objects.create(vehicle=self.vehicle, spot=self.spot)
        another_vehicle = Vehicle.objects.create(
            customer=self.customer, plate="XYZ9A87", model="Civic"
        )

        response = self.client.post(
            "/api/parking-sessions/",
            {"vehicle": another_vehicle.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserTestCase(TestCase):
    """Test Case example"""

    def setUp(self) -> None:
        self.name = "user_test_case"

    def test_user(self):
        """test example"""
        self.assertEqual(1, 1)
