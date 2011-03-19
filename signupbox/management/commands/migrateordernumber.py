#import psycopg2
#from psycopg2.extras import DictCursor 

#from django.core.management.base import BaseCommand, CommandError
#from django.db import transaction
#from django.contrib.auth.models import User

#from signupbox.constants import *
#from signupbox.models import Account, Event, Booking, Ticket, Field, FieldValue, FieldOption, Attendee
#from signupbox.signals import booking_confirmed

#class Command(BaseCommand):

    #def handle(self, *args, **options):
        #conn = psycopg2.connect(
              #"dbname = signupbox user = niels"
        #)

        #try:
            #transaction.enter_transaction_management()

            #account_cur = conn.cursor(cursor_factory=DictCursor)
            #account_cur.execute("SELECT * from accounts_account;")
            #for account in account_cur:
                #print 'fixing account %s' % account['name']

                ## create account
                #a, created = Account.objects.get_or_create(
                    #name=account['name']
                #)

                #event_cur = conn.cursor(cursor_factory=DictCursor)
                #event_cur.execute("SELECT * from core_event where account_id = %s;", (account['id'],))

                #for event in event_cur:
                    #print '\tfixing event %s' % event['title']

                    #e, created = Event.objects.get_or_create(
                        #account = a,
                        #title = event['title'],
                        #begins = event['start'],
                        #ends = event['end'],
                    #)

                    ## add bookings
                    #booking_cur = conn.cursor(cursor_factory=DictCursor)
                    #booking_cur.execute("SELECT * from core_booking where event_id = %s;", (event['id'],))
                    #for booking in booking_cur:
                        #try:
                            #b = Booking.objects.get(
                                #timestamp = booking['timestamp']
                            #)
                            #print b
                        #except Booking.DoesNotExist:
                            #print 'ouch'
                            #continue

            #transaction.commit()
        #finally:
            #transaction.leave_transaction_management()
        #print 'Successfully migrated signupbox!'
