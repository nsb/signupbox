from django.dispatch import Signal

booking_confirmed = Signal(providing_args=["booking_id",])