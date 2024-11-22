from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from random import randint
from datetime import datetime
from .branch import Branch

class Instructor(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('On Leave', 'On Leave'),
        ('Inactive', 'Inactive'),
        ('Archived', 'Archived')
    ]

    instructor_code = models.CharField(max_length=10, primary_key=True, editable=False)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    is_senior = models.BooleanField(default=False)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')

    def save(self, *args, **kwargs):
        if not self.instructor_code:
            self.generate_unique_instructor_code()
        
        if self.user:
            self.user.first_name = self.first_name
            self.user.last_name = self.last_name
            self.user.save()

        super().save(*args, **kwargs)

    def generate_unique_instructor_code(self):
        prefix = "INS"
        while True:
            unique_id = randint(1000, 9999)
            new_code = f'{prefix}-{unique_id}'
            if not Instructor.objects.filter(instructor_code=new_code).exists():
                self.instructor_code = new_code
                break

    def __str__(self):
        return f"{self.instructor_code}"
