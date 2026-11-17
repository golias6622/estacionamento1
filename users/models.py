from django.conf import settings
from django.db import models


class UserProfileExample(models.Model):
    phone_number = models.CharField(max_length=12)
    address = models.CharField(max_length=150)
    birth_date = models.DateField()
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"


class Customer(models.Model):
    name = models.CharField(max_length=120)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    class Meta:
        ordering = ["name", "id"]

    def __str__(self):
        return self.name


class Vehicle(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.PROTECT, related_name="vehicles"
    )
    plate = models.CharField(max_length=10, unique=True)
    make = models.CharField(max_length=60, blank=True)
    model = models.CharField(max_length=60)
    color = models.CharField(max_length=30, blank=True)

    class Meta:
        ordering = ["plate"]

    def __str__(self):
        return f"{self.plate} - {self.model}"


class ParkingSpot(models.Model):
    number = models.PositiveIntegerField(unique=True)

    class Meta:
        ordering = ["number"]

    def __str__(self):
        return f"Vaga {self.number}"

    @property
    def is_available(self):
        return not self.parking_sessions.filter(exit_at__isnull=True).exists()


class ParkingSession(models.Model):
    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.PROTECT, related_name="parking_sessions"
    )
    spot = models.ForeignKey(
        ParkingSpot, on_delete=models.PROTECT, related_name="parking_sessions"
    )
    entry_at = models.DateTimeField(auto_now_add=True)
    exit_at = models.DateTimeField(null=True, blank=True)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, default=10)
    amount_charged = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    class Meta:
        ordering = ["-entry_at"]

    def __str__(self):
        return f"{self.vehicle.plate} - {self.entry_at:%Y-%m-%d %H:%M}"
