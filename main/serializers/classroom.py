from rest_framework import serializers
from ..models import Classroom


class ClassroomSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.branch_name', read_only=True)

    class Meta:
        model = Classroom
        fields = ['classroom_code', 'capacity', 'branch', 'branch_name', 'status']
