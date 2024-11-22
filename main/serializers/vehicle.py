from rest_framework import serializers
from ..models import Vehicle


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['vehicle_code', 'wheel_num', 'transmission_type', 'vehicle_model', 'color', 'manufacturer', 'branch', 'status']