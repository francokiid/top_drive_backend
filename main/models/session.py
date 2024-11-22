from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from .enrollment import Enrollment
from .instructor import Instructor
from .facility import Facility
import math

class Session(models.Model):
    SESSION_NTH_CHOICES = [
        ('EXT', 'Extension'),
        ('ASS', 'Assessment'),
    ]

    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled'),
        ('Completed', 'Completed'),
        ('Missed', 'Missed'),
        ('Cancelled', 'Cancelled'),
        ('Archived', 'Archived')
    ]

    session_id = models.AutoField(primary_key=True)
    session_nth = models.CharField(
        max_length=5,
        validators=[
            RegexValidator(
                regex=r'^\d+$|^(EXT|ASS)$',
                message=_("Session nth must be a number or 'EXT'/'ASS'.")
            )
        ]
    )
    session_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    facility = models.ForeignKey(Facility, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Scheduled')

    def clean(self):
        if self.facility is None:
            raise ValidationError(_('Facility is required for a session.'))

        course_category = self.enrollment.course.course_category.category_type
        if course_category == 'PDC' and self.facility.facility_type != 'Vehicle':
            raise ValidationError(_('For PDC courses, the facility must be a vehicle.'))

        if course_category == 'TDC' and self.facility.facility_type != 'Classroom':
            raise ValidationError(_('For TDC courses, the facility must be a classroom.'))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        
        self.update_session_nth()
        self.update_enrollment_status()

    def update_session_nth(self):
        sessions = Session.objects.filter(
            enrollment=self.enrollment, 
            status__in=['Scheduled', 'Completed']
        ).order_by('session_date', 'start_time')

        for i, session in enumerate(sessions):
            session.session_nth = str(i + 1)

        Session.objects.bulk_update(sessions, ['session_nth'])

    def update_enrollment_status(self):
        enrollment = self.enrollment
        course_category = self.enrollment.course.course_category.category_type

        if course_category == 'PDC':
            total_sessions = math.ceil(enrollment.total_hours / 2)
        elif course_category == 'TDC':
            total_sessions = math.ceil(enrollment.total_hours / 7.5)
        else:
            total_sessions = 0

        scheduled_sessions = Session.objects.filter(enrollment=enrollment, status='Scheduled').count()
        completed_sessions = Session.objects.filter(enrollment=enrollment, status='Completed').count()
        missed_sessions = Session.objects.filter(enrollment=enrollment, status='Missed').count()
        cancelled_sessions = Session.objects.filter(enrollment=enrollment, status='Cancelled').count()

        if total_sessions == 0:
            enrollment.status = 'Awaiting Action'
        elif scheduled_sessions + completed_sessions < total_sessions:
            enrollment.status = 'Awaiting Follow-Up'
        elif completed_sessions == total_sessions:
            enrollment.status = 'Completed'
        elif completed_sessions > 0 and completed_sessions < total_sessions:
            enrollment.status = 'In Progress'
        elif scheduled_sessions == total_sessions:
            enrollment.status = 'All Sessions Scheduled'
        elif missed_sessions > 0 or cancelled_sessions > 0:
            enrollment.status = 'Awaiting Follow-Up'
        else:
            enrollment.status = 'Awaiting Action'

        enrollment.save()

    def __str__(self):
        return f'Session {self.session_id}'
