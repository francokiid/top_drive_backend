# Generated by Django 5.1.1 on 2024-11-24 01:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0020_alter_student_last_name_alter_student_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enrollment',
            name='enrollment_id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
