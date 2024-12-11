from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from datetime import datetime
from ..pagination import StandardResultsSetPagination
from ..models import Classroom, Session
from ..serializers import ClassroomSerializer


class ClassroomList(generics.ListCreateAPIView):
    queryset = Classroom.objects.exclude(status='Archived')
    serializer_class = ClassroomSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ['branch']
    search_fields = ['classroom_code', 'capacity', 'status', 'branch__branch_name']
    ordering_fields = '__all__'
    ordering = 'classroom_code'
    
    def get_queryset(self):
        queryset = Classroom.objects.all()
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
                facility__facility_type='Classroom'
            )

            busy_classrooms = set()
            for session in busy_sessions:
                try:
                    classroom = Classroom.objects.get(classroom_code=session.facility.object_id)
                    busy_count = busy_sessions.filter(facility=session.facility).count()
                    if busy_count >= classroom.capacity:
                        busy_classrooms.add(classroom.classroom_code)
                except Classroom.DoesNotExist:
                    continue

            queryset = queryset.exclude(classroom_code__in=busy_classrooms)

        return queryset


class ClassroomDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Classroom.objects.exclude(status='Archived')
    serializer_class = ClassroomSerializer
    lookup_field = 'classroom_code'
