# Generated by Django 5.1.1 on 2024-11-23 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0018_alter_enrollment_enrollment_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enrollment',
            name='enrollment_id',
            field=models.CharField(editable=False, max_length=6, primary_key=True, serialize=False),
        ),
    ]
