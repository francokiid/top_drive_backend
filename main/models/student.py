from django.db import models
from django.conf import settings
from random import randint
from django.utils.timezone import now

class Student(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Archived', 'Archived')
    ]

    student_code = models.CharField(max_length=10, primary_key=True, editable=False)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        help_text="Optional: Link to a user account."
    )
    year_joined = models.PositiveIntegerField(default=now().year)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='Active')

    def save(self, *args, **kwargs):
        if not self.student_code:
            self.generate_unique_student_code()
        
        if self.user:
            self.first_name = self.user.first_name
            self.last_name = self.user.last_name
        
        super().save(*args, **kwargs)

    def generate_unique_student_code(self):
        year = str(self.year_joined)[-2:]
        while True:
            unique_id = randint(10000, 99999)
            new_code = f'{year}-{unique_id}'
            if not Student.objects.filter(student_code=new_code).exists():
                self.student_code = new_code
                break

    def __str__(self):
        return f"{self.first_name}"