from django.db import models

class CourseCategory(models.Model):
    TYPE_CHOICES = [
        ('PDC', 'Practical Driving Course'),
        ('TDC', 'Theoretical Driving Course'),
    ]

    category_code = models.CharField(primary_key=True, max_length=10)
    category_name = models.CharField(max_length=255)
    category_type = models.CharField(max_length=25, choices=TYPE_CHOICES)

    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name_plural = "Course Categories"