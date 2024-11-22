from rest_framework import serializers
from ..models import Course


class CourseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='course_category.category_name', read_only=True)

    class Meta:
        model = Course
        fields = ['course_code', 'course_name', 'course_category', 'category_name', 'course_description', 'status']
