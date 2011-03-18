import psycopg2
from psycopg2.extras import DictCursor 

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.contrib.auth.models import User

from objperms.models import ObjectPermission
from signupbox.models import Account, Event, Booking, Ticket, Field, FieldValue, FieldOption, Attendee
from signupbox.signals import booking_confirmed

class Command(BaseCommand):

    def handle(self, *args, **options):
        conn = psycopg2.connect(
              "dbname = signupbox user = niels"
        )

        try:
            transaction.enter_transaction_management()

            user_cur = conn.cursor(cursor_factory=DictCursor)
            user_cur.execute("SELECT * from auth_user;")
            for user in user_cur:
                print 'adding user %s' % user['username']
                u, created = User.objects.get_or_create(
                    username = user['username'],
                )
                u.email = user['email']
                u.first_name = user['first_name']
                u.last_name = user['last_name']
                u.password = user['password']
                u.save()

            account_cur = conn.cursor(cursor_factory=DictCursor)
            account_cur.execute("SELECT * from accounts_account;")
            for account in account_cur:
                print 'adding account %s' % account['name']

                # create account
                a, created = Account.objects.get_or_create(
                    name=account['name']
                )
                a.organization = account['organization']
                a.street = account['street']
                a.zip_code = account['zip_code']
                a.city = account['city']
                a.phone = account['phone']
                a.email = account['email']
                a.cvr = account['cvr']
                a.payment_gateway = account['payment_gateway']
                a.merchant_id = account['merchant_id']
                a.secret_key = account['secret_key']
                a.domain = account['domain']
                a.extra_info = account['extra_info']
                a.terms = account['terms']
                a.autocapture = account['autocapture']
                a.google_analytics = account['google_analytics']
                a.save()

                account_user_cur = conn.cursor(cursor_factory=DictCursor)

                account_user_cur.execute(
                    """select username from auth_user, accounts_account, accounts_account_users
                       where auth_user.id = user_id 
                       and accounts_account.id = account_id and accounts_account.name = %s;""", (a.name,)
                )
                for user in account_user_cur:
                    a.users.add(User.objects.get(username=user['username']))
                    obj_perm, created = ObjectPermission.objects.get_or_create(
                        user = user, content_object = a,
                    )
                    obj_perm.can_view = True
                    obj_perm.can_change = True
                    obj_perm.can_delete = True
                    obj_per.save()

                event_cur = conn.cursor(cursor_factory=DictCursor)
                event_cur.execute("SELECT * from core_event where account_id = %s;", (account['id'],))

                for event in event_cur:
                    print '\tadding event %s' % event['title']

                    e, created = Event.objects.get_or_create(
                        account = a,
                        title = event['title'],
                        begins = event['start'],
                        ends = event['end'],
                    )
                    e.description = event['description']
                    e.venue = event['venue']
                    e.address = event['address']
                    e.city = event['city']
                    e.zip_code = event['zip_code']
                    e.capacity = event['capacity']
                    e.status = event['status']
                    e.currency = event['currency']
                    e.save()

                    # add tickets
                    e.tickets.all().delete()
                    e.tickets.add(
                        Ticket.objects.create(
                            event=e,
                            name='Standard billet',
                            price=event['price']
                        )
                    )

                    # add fields
                    e.fields.all().delete()
                    field_cur = conn.cursor(cursor_factory=DictCursor)
                    field_cur.execute("SELECT * from core_formfield where event_id = %s;", (event['id'],))
                    for field in field_cur:
                        f = Field.objects.create(
                            event = e,
                            label = field['label'],
                            help_text = field['help_text'],
                            required = field['required'],
                            in_extra = field['in_extra'],
                            ordering = field['order'],
                            type = field['field_type'],
                        )

                        # add field options
                        field_option_cur = conn.cursor(cursor_factory=DictCursor)
                        field_option_cur.execute("SELECT * from core_choicevalue where parent_id = %s;", (field['id'],))
                        for field_option in field_option_cur:
                            FieldOption.objects.create(
                                field = f,
                                value = field_option['value'],
                            )


                    # add bookings
                    e.bookings.all().delete()
                    booking_cur = conn.cursor(cursor_factory=DictCursor)
                    booking_cur.execute("SELECT * from core_booking where event_id = %s;", (event['id'],))
                    for booking in booking_cur:
                        b = Booking.objects.create(
                            event = e,
                            notes = booking['notes'],
                            description = booking['description'],
                            transaction = booking['transaction'],
                            cardtype = booking['cardtype'],
                            amount = booking['amount'],
                            currency = booking['currency'],
                            confirmed = True,
                        )
                        b.timestamp = booking['timestamp']
                        b.save()

                        # add attendees
                        attendee_cur = conn.cursor(cursor_factory=DictCursor)
                        attendee_cur.execute("SELECT * from core_registration where booking_id = %s;", (booking['id'],))
                        ticket = e.tickets.get()
                        for attendee in attendee_cur:
                            at = Attendee.objects.create(
                                account = a,
                                booking = b,
                                ticket = ticket,
                                attendee_count = attendee['num_attendees'],
                            )

                            # add field values
                            field_value_cur = conn.cursor(cursor_factory=DictCursor)
                            field_value_cur.execute("SELECT * from core_registrationdata, core_formfield where registration_id = %s and field_id = core_formfield.id;", (attendee['id'],))
                            for field_value in field_value_cur:
                                FieldValue.objects.create(
                                    attendee = at,
                                    field = e.fields.get(ordering=field_value['order']),
                                    value = field_value['value']
                                )

                        #booking_confirmed.send(sender=b, booking_id=b.id)

            transaction.commit()
        finally:
            transaction.leave_transaction_management()
        print 'Successfully migrated signupbox!'
