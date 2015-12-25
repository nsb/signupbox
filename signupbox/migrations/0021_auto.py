# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding M2M table for field subscribers on 'Event'
        db.create_table('signupbox_event_subscribers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('event', models.ForeignKey(orm['signupbox.event'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('signupbox_event_subscribers', ['event_id', 'user_id'])


    def backwards(self, orm):
        
        # Removing M2M table for field subscribers on 'Event'
        db.delete_table('signupbox_event_subscribers')


    models = {
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
            'from_address': ('django.db.models.fields.EmailField', [], {'max_length': '254', 'blank': 'True'}),
            'genitive_organization': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'google_analytics': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'groups'", 'blank': 'True', 'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'merchant_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'organization': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'payment_gateway': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'paypal_business': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'relationwise_survey_id': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'reply_to': ('django.db.models.fields.EmailField', [], {'max_length': '254', 'blank': 'True'}),
            'script_codes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'secret_key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'sms_gateway': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'sms_gateway_password': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'sms_gateway_username': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
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
            'Meta': {'ordering': "('id',)", 'object_name': 'Attendee'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attendees'", 'to': "orm['signupbox.Account']"}),
            'attendee_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'booking': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attendees'", 'to': "orm['signupbox.Booking']"}),
            'fields': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['signupbox.Field']", 'through': "orm['signupbox.FieldValue']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reminder_sent': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
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
            'ordernumber': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'token': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'db_index': 'True'}),
            'transaction': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'signupbox.event': {
            'Meta': {'ordering': "['begins', 'title', 'slug']", 'unique_together': "(('account', 'slug'),)", 'object_name': 'Event'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'events'", 'to': "orm['signupbox.Account']"}),
            'address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'begins': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'capacity': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'default': "'DKK'", 'max_length': '3', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'ends': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'da'", 'max_length': '2'}),
            'project_id': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'reminder': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'reminder_subject': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'blank': 'True'}),
            'reminders_sent': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'send_reminder': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'db_index': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'open'", 'max_length': '32', 'db_index': 'True'}),
            'subscribers': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'events'", 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'events'", 'null': 'True', 'to': "orm['signupbox.RelationWiseSurvey']"}),
            'surveyEnabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'surveySent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'venue': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'signupbox.field': {
            'Meta': {'ordering': "('ordering', 'id')", 'unique_together': "(('event', 'name'),)", 'object_name': 'Field'},
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
        'signupbox.relationwisesurvey': {
            'Meta': {'object_name': 'RelationWiseSurvey'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'surveys'", 'to': "orm['signupbox.Account']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'survey_id': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'signupbox.ticket': {
            'Meta': {'object_name': 'Ticket'},
            'available': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
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
