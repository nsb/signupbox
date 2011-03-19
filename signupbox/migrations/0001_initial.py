# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Account'
        db.create_table('signupbox_account', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('organization', self.gf('django.db.models.fields.CharField')(max_length=1024, blank=True)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('zip_code', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('cvr', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
            ('payment_gateway', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('merchant_id', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('secret_key', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('paypal_business', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('autocapture', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('domain', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('extra_info', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('terms', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('google_analytics', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'], blank=True)),
        ))
        db.send_create_signal('signupbox', ['Account'])

        # Adding M2M table for field users on 'Account'
        db.create_table('signupbox_account_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('account', models.ForeignKey(orm['signupbox.account'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('signupbox_account_users', ['account_id', 'user_id'])

        # Adding M2M table for field groups on 'Account'
        db.create_table('signupbox_account_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('account', models.ForeignKey(orm['signupbox.account'], null=False)),
            ('group', models.ForeignKey(orm['auth.group'], null=False))
        ))
        db.create_unique('signupbox_account_groups', ['account_id', 'group_id'])

        # Adding model 'AccountInvite'
        db.create_table('signupbox_accountinvite', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(related_name='invites', to=orm['signupbox.Account'])),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=128)),
            ('is_admin', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_accepted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('expires', self.gf('django.db.models.fields.DateTimeField')()),
            ('invited_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('signupbox', ['AccountInvite'])

        # Adding model 'Profile'
        db.create_table('signupbox_profile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], unique=True)),
        ))
        db.send_create_signal('signupbox', ['Profile'])

        # Adding model 'Event'
        db.create_table('signupbox_event', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255, db_index=True)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(related_name='events', to=orm['signupbox.Account'])),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('venue', self.gf('django.db.models.fields.CharField')(max_length=1024, blank=True)),
            ('begins', self.gf('django.db.models.fields.DateTimeField')()),
            ('ends', self.gf('django.db.models.fields.DateTimeField')()),
            ('capacity', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='open', max_length=32, db_index=True)),
            ('currency', self.gf('django.db.models.fields.CharField')(default='DKK', max_length=3, blank=True)),
        ))
        db.send_create_signal('signupbox', ['Event'])

        # Adding unique constraint on 'Event', fields ['account', 'slug']
        db.create_unique('signupbox_event', ['account_id', 'slug'])

        # Adding model 'Ticket'
        db.create_table('signupbox_ticket', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tickets', to=orm['signupbox.Event'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1024, blank=True)),
            ('offered_from', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('offered_to', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('price', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=7, decimal_places=2)),
        ))
        db.send_create_signal('signupbox', ['Ticket'])

        # Adding model 'Booking'
        db.create_table('signupbox_booking', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(related_name='bookings', to=orm['signupbox.Event'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1024, blank=True)),
            ('transaction', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('cardtype', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=7, decimal_places=2)),
            ('currency', self.gf('django.db.models.fields.CharField')(max_length=3, blank=True)),
            ('confirmed', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('signupbox', ['Booking'])

        # Adding model 'Field'
        db.create_table('signupbox_field', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(related_name='fields', null=True, to=orm['signupbox.Event'])),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('help_text', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(default='text', max_length=255)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('in_extra', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('ordering', self.gf('django.db.models.fields.IntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=36, blank=True)),
        ))
        db.send_create_signal('signupbox', ['Field'])

        # Adding unique constraint on 'Field', fields ['event', 'name']
        db.create_unique('signupbox_field', ['event_id', 'name'])

        # Adding model 'Attendee'
        db.create_table('signupbox_attendee', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(related_name='attendees', to=orm['signupbox.Account'])),
            ('booking', self.gf('django.db.models.fields.related.ForeignKey')(related_name='attendees', to=orm['signupbox.Booking'])),
            ('ticket', self.gf('django.db.models.fields.related.ForeignKey')(related_name='attendees', to=orm['signupbox.Ticket'])),
            ('status', self.gf('django.db.models.fields.CharField')(default='confirmed', max_length=32)),
            ('attendee_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
        ))
        db.send_create_signal('signupbox', ['Attendee'])

        # Adding model 'FieldValue'
        db.create_table('signupbox_fieldvalue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('attendee', self.gf('django.db.models.fields.related.ForeignKey')(related_name='values', to=orm['signupbox.Attendee'])),
            ('field', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['signupbox.Field'])),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=1024, blank=True)),
        ))
        db.send_create_signal('signupbox', ['FieldValue'])

        # Adding model 'FieldOption'
        db.create_table('signupbox_fieldoption', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('field', self.gf('django.db.models.fields.related.ForeignKey')(related_name='options', to=orm['signupbox.Field'])),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=512)),
        ))
        db.send_create_signal('signupbox', ['FieldOption'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Field', fields ['event', 'name']
        db.delete_unique('signupbox_field', ['event_id', 'name'])

        # Removing unique constraint on 'Event', fields ['account', 'slug']
        db.delete_unique('signupbox_event', ['account_id', 'slug'])

        # Deleting model 'Account'
        db.delete_table('signupbox_account')

        # Removing M2M table for field users on 'Account'
        db.delete_table('signupbox_account_users')

        # Removing M2M table for field groups on 'Account'
        db.delete_table('signupbox_account_groups')

        # Deleting model 'AccountInvite'
        db.delete_table('signupbox_accountinvite')

        # Deleting model 'Profile'
        db.delete_table('signupbox_profile')

        # Deleting model 'Event'
        db.delete_table('signupbox_event')

        # Deleting model 'Ticket'
        db.delete_table('signupbox_ticket')

        # Deleting model 'Booking'
        db.delete_table('signupbox_booking')

        # Deleting model 'Field'
        db.delete_table('signupbox_field')

        # Deleting model 'Attendee'
        db.delete_table('signupbox_attendee')

        # Deleting model 'FieldValue'
        db.delete_table('signupbox_fieldvalue')

        # Deleting model 'FieldOption'
        db.delete_table('signupbox_fieldoption')


    models = {
        'activities.activity': {
            'Meta': {'ordering': "('-timestamp',)", 'object_name': 'Activity'},
            'activity': ('django.db.models.fields.CharField', [], {'max_length': '1028'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'signupbox.account': {
            'Meta': {'object_name': 'Account'},
            'autocapture': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'cvr': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'domain': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'extra_info': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'google_analytics': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'groups'", 'blank': 'True', 'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'merchant_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'organization': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'payment_gateway': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'paypal_business': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'secret_key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']", 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'terms': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'accounts'", 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'signupbox.accountinvite': {
            'Meta': {'object_name': 'AccountInvite'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invites'", 'to': "orm['signupbox.Account']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '128'}),
            'expires': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invited_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'is_accepted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'signupbox.attendee': {
            'Meta': {'ordering': "('-id',)", 'object_name': 'Attendee'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attendees'", 'to': "orm['signupbox.Account']"}),
            'attendee_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'booking': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attendees'", 'to': "orm['signupbox.Booking']"}),
            'fields': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['signupbox.Field']", 'through': "orm['signupbox.FieldValue']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'confirmed'", 'max_length': '32'}),
            'ticket': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attendees'", 'to': "orm['signupbox.Ticket']"})
        },
        'signupbox.booking': {
            'Meta': {'object_name': 'Booking'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '7', 'decimal_places': '2'}),
            'cardtype': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '3', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bookings'", 'to': "orm['signupbox.Event']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'transaction': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'signupbox.event': {
            'Meta': {'ordering': "['begins', 'title', 'slug']", 'unique_together': "(('account', 'slug'),)", 'object_name': 'Event'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'events'", 'to': "orm['signupbox.Account']"}),
            'begins': ('django.db.models.fields.DateTimeField', [], {}),
            'capacity': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'default': "'DKK'", 'max_length': '3', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'ends': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'db_index': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'open'", 'max_length': '32', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'venue': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'})
        },
        'signupbox.field': {
            'Meta': {'ordering': "('id',)", 'unique_together': "(('event', 'name'),)", 'object_name': 'Field'},
            'event': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fields'", 'null': 'True', 'to': "orm['signupbox.Event']"}),
            'help_text': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_extra': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'}),
            'ordering': ('django.db.models.fields.IntegerField', [], {}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'text'", 'max_length': '255'})
        },
        'signupbox.fieldoption': {
            'Meta': {'ordering': "('id',)", 'object_name': 'FieldOption'},
            'field': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'options'", 'to': "orm['signupbox.Field']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        },
        'signupbox.fieldvalue': {
            'Meta': {'ordering': "('field',)", 'object_name': 'FieldValue'},
            'attendee': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'values'", 'to': "orm['signupbox.Attendee']"}),
            'field': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['signupbox.Field']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'})
        },
        'signupbox.profile': {
            'Meta': {'object_name': 'Profile'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'signupbox.ticket': {
            'Meta': {'object_name': 'Ticket'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tickets'", 'to': "orm['signupbox.Event']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'offered_from': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'offered_to': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '7', 'decimal_places': '2'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['signupbox']
