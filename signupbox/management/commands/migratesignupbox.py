import psycopg2
from psycopg2.extras import DictCursor 

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from django.contrib.auth.models import User
from signupbox.models import Account, Event, Ticket, Field, FieldValue, FieldOption

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
                            offered_from=e.begins,
                            offered_to=e.ends,
                            price=event['price']
                        )
                    )


                    e.fields.all().delete()
                    field_cur = conn.cursor(cursor_factory=DictCursor)
                    field_cur.execute("SELECT * from core_formfield where event_id = %s;", (event['id'],))
                    for field in field_cur:
                        Field.objects.create(
                            event = e,
                            label = field['label'],
                            help_text = field['help_text'],
                            required = field['required'],
                            in_extra = field['in_extra'],
                            ordering = field['order']
                        )

            transaction.commit()
        finally:
            transaction.leave_transaction_management()
        print 'Successfully migrated signupbox!'
