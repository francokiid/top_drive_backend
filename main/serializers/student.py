from rest_framework import serializers
from ..models import Student, Enrollment, Session


class StudentSerializer(serializers.ModelSerializer):
    email = serializers.CharField(source='user.email', read_only=True)
    is_active = serializers.BooleanField(source='user.is_active', read_only=True)
    courses_enrolled = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = ['student_code', 'first_name', 'last_name', 'address', 'contact_number', 'emergency_number', 'email', 'is_active', 'year_joined', 'status', 'courses_enrolled']

    def get_courses_enrolled(self, obj):
        enrollments = Enrollment.objects.filter(student=obj)
        courses_data = []
        
        for enrollment in enrollments:
            course_code = enrollment.course.course_code
            course_category = enrollment.course.course_category.category_code
            total_hours = enrollment.total_hours

            if course_code == 'ASS':
                total_sessions = 1
            elif course_category in ['4W', '2W/3W', 'SDC']:
                total_sessions = total_hours // 2
            elif course_category == 'TDC':
                total_sessions = int(total_hours // 7.5)
            else:
                total_sessions = 0
                
            scheduled_sessions = Session.objects.filter(
                enrollment=enrollment,
                status__in=['Scheduled', 'Completed']
            ).count()

            completed_sessions = Session.objects.filter(
                enrollment=enrollment,
                status='Completed'
            ).count()
            
            courses_data.append({
                'course_code': enrollment.course.course_code, 
                'course_name': enrollment.course.course_name,
                'total_hours': enrollment.total_hours,
                'transmission_type': enrollment.transmission_type,
                'course_category': enrollment.course.course_category.category_name,
                'enrollment_status': enrollment.status,
                'total_sessions': total_sessions,
                'scheduled_sessions': scheduled_sessions,
                'completed_sessions': completed_sessions,
            })
        
        return courses_data
