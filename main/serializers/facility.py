from rest_framework import serializers
from ..models import Facility

class FacilitySerializer(serializers.ModelSerializer):
    facility = serializers.PrimaryKeyRelatedField(queryset=Facility.objects.all(), required=False)

    class Meta:
        model = Facility
        fields = ['id', 'facility', 'facility_type', 'content_type', 'object_id']