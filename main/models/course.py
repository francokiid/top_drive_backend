from django.db import models
from .course_category import CourseCategory

class Course(models.Model):
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('Closed', 'Closed'),
        ('Archived', 'Archived')
    ]

    course_code = models.CharField(primary_key=True, max_length=10)
    course_name = models.CharField(max_length=255)
    course_category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE)
    course_description = models.CharField(max_length=500)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='Open')

    def __str__(self):
        return self.course_name
