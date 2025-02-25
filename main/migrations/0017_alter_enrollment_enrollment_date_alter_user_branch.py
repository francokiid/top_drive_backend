# Generated by Django 5.1.1 on 2024-11-21 05:34

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_user_branch_alter_enrollment_enrollment_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enrollment',
            name='enrollment_date',
            field=models.DateField(default=datetime.date(2024, 11, 21)),
        ),
        migrations.AlterField(
            model_name='user',
            name='branch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.branch'),
        ),
    ]
