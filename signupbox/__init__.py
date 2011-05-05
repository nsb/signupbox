from django.conf import settings

from models import Booking

from tasks import process_booking

from signals import booking_confirmed

def on_booking_confirmed(sender, booking_id, **kwargs):

    booking = Booking.objects.get(pk=booking_id)
    booking.confirmed = True
    booking.cardtype = kwargs.get("cardtype", "")
    booking.save()

    process_booking.delay(booking, settings.LANGUAGE_CODE)

booking_confirmed.connect(on_booking_confirmed)
