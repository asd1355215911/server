# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding index on 'Property', fields ['key']
        db.create_index('Users_property', ['key'])

        # Changing field 'ServiceUser.last_login'
        db.alter_column('Users_serviceuser', 'last_login', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True))

        # Changing field 'ServiceUser.date_joined'
        db.alter_column('Users_serviceuser', 'date_joined', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True))


    def backwards(self, orm):
        
        # Removing index on 'ServiceUser', fields ['username']
        db.delete_index('Users_serviceuser', ['username'])

        # Removing index on 'Property', fields ['key']
        db.delete_index('Users_property', ['key'])

        # Changing field 'ServiceUser.last_login'
        db.alter_column('Users_serviceuser', 'last_login', self.gf('django.db.models.fields.DateTimeField')(auto_now=True))

        # Changing field 'ServiceUser.date_joined'
        db.alter_column('Users_serviceuser', 'date_joined', self.gf('django.db.models.fields.DateTimeField')())


    models = {
        'Users.property': {
            'Meta': {'unique_together': "(('user', 'key'),)", 'object_name': 'Property'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['Users.ServiceUser']"}),
            'value': ('django.db.models.fields.TextField', [], {})
        },
        'Users.serviceuser': {
            'Meta': {'object_name': 'ServiceUser'},
            'algorithm': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'hash': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'salt': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '60', 'db_index': 'True'})
        }
    }

    complete_apps = ['Users']
