# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.db import models, migrations

class Migration(migrations.Migration):

    dependencies = [
        (settings.PUSH_DEVICE_OWNER_MODEL.split(".")[0], "0001_initial")
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('owner', models.ForeignKey(to=settings.PUSH_DEVICE_OWNER_MODEL)),
                ('registration_id', models.CharField(max_length=200)),
                ('platform', models.CharField(max_length=30, choices=[("ios","iOS"),("android","Android")]))
            ],
            bases=(models.Model,),
        )
    ]
