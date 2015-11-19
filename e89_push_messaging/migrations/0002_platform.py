# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('e89_push_messaging', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='version',
            field=models.CharField(max_length=30, null=True),
        )
    ]
