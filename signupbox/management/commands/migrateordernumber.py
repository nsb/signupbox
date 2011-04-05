import psycopg2
from psycopg2.extras import DictCursor 

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.contrib.auth.models import User

from signupbox.constants import *
from signupbox.models import Booking

class Command(BaseCommand):

    def handle(self, *args, **options):
        conn = psycopg2.connect(
            "dbname = signupbox_old user = niels"
        )

        try:
            transaction.enter_transaction_management()

            booking_cur = conn.cursor(cursor_factory=DictCursor)
            booking_cur.execute("SELECT * from core_booking;")
            for booking in booking_cur:
                try:
                    b = Booking.objects.get(
                        transaction=booking['transaction'],
                        ordernumber=1
                    )
                    b.ordernumber = booking['ordernum']
                    b.save()
                    print "updated booking %s with ordernumber %s" % (b, booking['ordernum'])
                except (Booking.DoesNotExist, Booking.MultipleObjectsReturned):
                    continue

            transaction.commit()
        finally:
            transaction.leave_transaction_management()
        print 'Successfully migrated signupbox!'
