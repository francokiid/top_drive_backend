# Generated by Django 5.1.1 on 2024-11-13 13:06

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_alter_branch_status_alter_classroom_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enrollment',
            name='enrollment_date',
            field=models.DateField(default=datetime.date(2024, 11, 13)),
        ),
    ]
