from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Facility(models.Model):
    FACILITY_TYPE_CHOICES = [
        ('Vehicle', 'Vehicle'),
        ('Classroom', 'Classroom'),
    ]

    facility_type = models.CharField(max_length=10, choices=FACILITY_TYPE_CHOICES)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField()
    facility = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"{self.object_id}"
