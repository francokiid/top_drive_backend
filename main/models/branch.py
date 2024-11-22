from django.db import models

class Branch(models.Model):
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('Closed', 'Closed'),
        ('Archived', 'Archived')
    ]

    branch_name = models.CharField(primary_key=True, max_length=50)
    branch_address = models.CharField(max_length=255)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='Active')

    def __str__(self):
        return self.branch_name

    class Meta: 
        verbose_name_plural = "Branches"