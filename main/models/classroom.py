from django.db import models
from .branch import Branch
from .facility import Facility
from django.contrib.contenttypes.models import ContentType

class Classroom(models.Model):
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Unavailable', 'Unavailable'),
        ('Archived', 'Archived')
    ]

    classroom_code = models.CharField(max_length=10, primary_key=True, editable=False)
    capacity = models.PositiveIntegerField()
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='Available')

    def generate_unique_classroom_code(self):
        prefix = "RM"
        existing_codes = Classroom.objects.filter(classroom_code__startswith=prefix).values_list('classroom_code', flat=True)
        numeric_parts = [
            int(code.split('-')[1]) for code in existing_codes if code.split('-')[1].isdigit()
        ]
        next_number = max(numeric_parts, default=100) + 1
        self.classroom_code = f'{prefix}-{next_number}'

    def save(self, *args, **kwargs):
        if not self.classroom_code:
            self.generate_unique_classroom_code()
        super(Classroom, self).save(*args, **kwargs)
        Facility.objects.get_or_create(
            facility_type='Classroom',
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.classroom_code,
        )

    def delete(self, *args, **kwargs):
        Facility.objects.filter(content_type=ContentType.objects.get_for_model(self), object_id=self.classroom_code).delete()
        super(Classroom, self).delete(*args, **kwargs)

    def __str__(self):
        return f'{self.classroom_code} / {self.branch.branch_name}'
