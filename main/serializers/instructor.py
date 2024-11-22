from rest_framework import serializers
from ..models import Instructor


class InstructorSerializer(serializers.ModelSerializer):
    email = serializers.CharField(source='user.email', read_only=True)
    branch_name = serializers.CharField(source='branch.branch_name', read_only=True)

    class Meta:
        model = Instructor
        fields = ['instructor_code', 'first_name', 'last_name', 'email', 'is_senior', 'branch', 'branch_name', 'status']
        