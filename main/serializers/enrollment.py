from rest_framework import serializers
from ..models import Enrollment, Session

class EnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.first_name', read_only=True)
    course_code = serializers.CharField(source='course.course_code', read_only=True)
    course_name = serializers.CharField(source='course.course_name', read_only=True)
    course_category = serializers.CharField(source='course.course_category', read_only=True)
    branch_name = serializers.CharField(source='branch.branch_name', read_only=True)
    scheduled_sessions = serializers.SerializerMethodField()
    completed_sessions = serializers.SerializerMethodField()


    class Meta:
        model = Enrollment
        fields = [
            'enrollment_id', 'enrollment_date', 'branch', 'branch_name', 'student', 'student_name', 
            'course', 'course_code', 'course_name', 'course_category', 'transmission_type', 'total_hours', 
            'preferred_dates', 'remarks', 'status', 'scheduled_sessions', 'completed_sessions'
        ]

    def get_scheduled_sessions(self, obj):
        return Session.objects.filter(
            enrollment=obj,
            status__in = ['Scheduled', 'Completed']
        ).count()

    def get_completed_sessions(self, obj):
        return Session.objects.filter(
            enrollment=obj,
            status='Completed'
        ).count()
