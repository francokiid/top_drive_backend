# Generated by Django 5.1.1 on 2024-11-14 12:41

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_alter_enrollment_enrollment_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enrollment',
            name='enrollment_date',
            field=models.DateField(default=datetime.date(2024, 11, 14)),
        ),
    ]
