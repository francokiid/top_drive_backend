from datetime import datetime, time as dt_time
from django.db.models import Q
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from ..pagination import StandardResultsSetPagination
from ..models import Vehicle, Session
from ..serializers import VehicleSerializer

class VehicleList(generics.ListCreateAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ['branch']
    search_fields = ['vehicle_code', 'vehicle_model', 'manufacturer', 'color', 'wheel_num', 'transmission_type', 'status', 'branch__branch_name']
    ordering_fields = '__all__'
    ordering = 'vehicle_code'

    def get_queryset(self):
        queryset = Vehicle.objects.all()
        date = self.request.query_params.get('date', None)
        start_time = self.request.query_params.get('start_time', None)
        end_time = self.request.query_params.get('end_time', None)

        if date and start_time:
            start_datetime = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
            
            if end_time:
                end_datetime = datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M")
            else:
                end_datetime = datetime.strptime(f"{date} 23:59", "%Y-%m-%d %H:%M")

            busy_sessions = Session.objects.filter(
                session_date=start_datetime.date(),
                start_time__lt=end_datetime.time(),
                end_time__gt=start_datetime.time(),
                facility__facility_type='Vehicle'
            ).values_list('facility__object_id', flat=True)

            busy_vehicles = set(busy_sessions)

            queryset = queryset.exclude(vehicle_code__in=busy_vehicles)

        return queryset


    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class VehicleDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    lookup_field = 'vehicle_code'
