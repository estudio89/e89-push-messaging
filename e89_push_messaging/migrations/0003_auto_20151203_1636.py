# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('e89_push_messaging', '0002_platform'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='device',
            unique_together=set([('registration_id', 'platform')]),
        ),
    ]
