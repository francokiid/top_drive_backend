from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from ..pagination import StandardResultsSetPagination
from ..models import Classroom
from ..serializers import ClassroomSerializer


class ClassroomList(generics.ListCreateAPIView):
    queryset = Classroom.objects.exclude(status='Archived')
    serializer_class = ClassroomSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ['branch']
    search_fields = search_fields = ['classroom_code', 'capacity', 'branch', 'status']
    ordering_fields = '__all__'
    ordering = 'classroom_code'
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class ClassroomDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Classroom.objects.exclude(status='Archived')
    serializer_class = ClassroomSerializer
    lookup_field = 'classroom_code'
