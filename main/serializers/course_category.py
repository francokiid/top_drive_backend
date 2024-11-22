from rest_framework import serializers
from ..models import CourseCategory


class CourseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCategory
        fields = ['category_code', 'category_name', 'category_type']
