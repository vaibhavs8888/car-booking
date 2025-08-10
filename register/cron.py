from django.utils import timezone
from register.models import Car

def clear_expired_bookings():
    """Unblock cars whose booking time has expired."""
    now = timezone.now()
    expired_cars = Car.objects.filter(is_booked=True, available_from__lte=now)
    for car in expired_cars:
        car.is_booked = False
        car.available_from = None
        car.save()
    print(f"Cleared {expired_cars.count()} expired car bookings at {now}")