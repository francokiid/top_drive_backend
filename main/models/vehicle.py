from django.db import models
from django.contrib.contenttypes.models import ContentType
from .branch import Branch
from .facility import Facility

class Vehicle(models.Model):
    WHEEL_NUM_CHOICES = [
        ('2W', '2 Wheels'),
        ('3W', '3 Wheels'),
        ('4W', '4 Wheels'),
    ]

    TRANSMISSION_TYPE_CHOICES = [
        ('MT', 'Manual Transmission'),
        ('AT', 'Automatic Transmission'),
    ]

    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Unavailable', 'Unavailable'),
        ('Archived', 'Archived')
    ]

    vehicle_code = models.CharField(max_length=10, primary_key=True, editable=False)
    wheel_num = models.CharField(max_length=2, choices=WHEEL_NUM_CHOICES)
    transmission_type = models.CharField(max_length=2, choices=TRANSMISSION_TYPE_CHOICES)
    vehicle_model = models.CharField(max_length=255)
    color = models.CharField(max_length=50)
    manufacturer = models.CharField(max_length=255)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='Available')

    def generate_unique_vehicle_code(self):
        prefix_map = {
            ('MT', '2W'): 'M2',
            ('MT', '3W'): 'M3',
            ('MT', '4W'): 'M4',
            ('AT', '2W'): 'A2',
            ('AT', '3W'): 'A3',
            ('AT', '4W'): 'A4',
        }

        prefix = prefix_map.get((self.transmission_type, self.wheel_num), 'UNK')

        existing_codes = Vehicle.objects.filter(vehicle_code__startswith=prefix).values_list('vehicle_code', flat=True)
        numeric_suffixes = [
            int(code.split('-')[1]) for code in existing_codes if code.split('-')[1].isdigit()
        ]

        next_number = max(numeric_suffixes, default=0) + 1

        self.vehicle_code = f'{prefix}-{next_number:03}'

    def save(self, *args, **kwargs):
        if not self.vehicle_code:
            self.generate_unique_vehicle_code()
        super(Vehicle, self).save(*args, **kwargs)
        Facility.objects.get_or_create(
            facility_type='Vehicle',
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.vehicle_code,
        )

    def delete(self, *args, **kwargs):
        Facility.objects.filter(content_type=ContentType.objects.get_for_model(self), object_id=self.vehicle_code).delete()
        super(Vehicle, self).delete(*args, **kwargs)

    def __str__(self):
        return f"{self.vehicle_model} {self.transmission_type} {self.color} / {self.branch.branch_name}"
