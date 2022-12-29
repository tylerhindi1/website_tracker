# Generated by Django 4.1.4 on 2022-12-27 19:18

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0031_verificationcode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='verificationcode',
            name='expires_at',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='visitcount',
            name='last_visit_date',
            field=models.DateField(default=datetime.date(2022, 12, 28)),
        ),
    ]
