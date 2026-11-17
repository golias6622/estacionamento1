from django.contrib import admin

from users.models import Customer, ParkingSession, ParkingSpot, Vehicle

admin.site.register(Customer)
admin.site.register(Vehicle)
admin.site.register(ParkingSpot)
admin.site.register(ParkingSession)
