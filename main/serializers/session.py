from rest_framework import serializers
from ..models import Session, Facility, Vehicle, Classroom
from ..serializers import EnrollmentSerializer

class SessionSerializer(serializers.ModelSerializer):
    course = serializers.CharField(source='enrollment.course.course_code', read_only=True)
    course_name = serializers.CharField(source='enrollment.course.course_name', read_only=True)
    course_category = serializers.CharField(source='enrollment.course.course_category', read_only=True)
    transmission_type = serializers.CharField(source='enrollment.transmission_type', read_only=True)
    student = serializers.CharField(source='enrollment.student', read_only=True)
    student_code = serializers.CharField(source='enrollment.student.student_code', read_only=True)
    branch = serializers.CharField(source='enrollment.branch', read_only=True)
    instructor_name = serializers.SerializerMethodField()
    facility_code = serializers.CharField(source='facility.object_id', read_only=True)
    facility_name = serializers.SerializerMethodField()

    class Meta:
        model = Session
        fields = [
            'session_id', 'session_nth', 'session_date', 'start_time', 'end_time', 
            'enrollment', 'transmission_type', 'course', 'course_name', 
            'course_category', 'student', 'student_code', 'branch', 'instructor', 'instructor_name', 
            'facility', 'facility_code', 'facility_name', 'status'
        ]
    
    def get_instructor_name(self, obj):
        instructor = obj.instructor
        if instructor and instructor.branch:
            return f"{instructor.first_name} / {instructor.branch.branch_name}"
        return instructor.first_name if instructor else None

    def get_facility_name(self, obj):
        facility_model_map = {
            'Vehicle': Vehicle,
            'Classroom': Classroom
        }
        
        if obj.facility:
            model = facility_model_map.get(obj.facility.facility_type)
            if model:
                try:
                    facility_instance = model.objects.get(pk=obj.facility.object_id)
                    return str(facility_instance)
                except model.DoesNotExist:
                    return None
        return None
