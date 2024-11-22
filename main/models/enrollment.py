from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone
from .branch import Branch
from .student import Student
from .course import Course

class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('Awaiting Action', 'Awaiting Action'),
        ('Awaiting Follow-Up', 'Awaiting Follow-Up'),
        ('All Sessions Scheduled', 'All Sessions Scheduled'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Forfeited', 'Forfeited'),
        ('Archived', 'Archived')
    ]

    TRANSMISSION_TYPE_CHOICES = [
        ('MT', 'MT'),
        ('AT', 'AT'),
        ('NA', 'NA'),
    ]

    enrollment_id = models.AutoField(primary_key=True)
    enrollment_date = models.DateField(default=timezone.now)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    transmission_type = models.CharField(max_length=2, choices=TRANSMISSION_TYPE_CHOICES, default='NA')
    total_hours = models.PositiveIntegerField()
    preferred_dates = ArrayField(
        models.DateField(),
        blank=True,
        default=list,
        help_text="List of preferred dates for sessions."
    )
    remarks = models.TextField(blank=True, null=True, help_text="Additional comments or information related to the enrollment.")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Awaiting Action')

    def __str__(self):
        return str(self.enrollment_id)
