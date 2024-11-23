from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from ..pagination import StandardResultsSetPagination
from ..models import Course
from ..serializers import CourseSerializer


class CourseList(generics.ListCreateAPIView):
    queryset = Course.objects.exclude(status='Archived')
    serializer_class = CourseSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ['course_category']
    search_fields = ['course_code', 'course_name', 'status']
    ordering_fields = '__all__'
    ordering = 'course_code'

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class CourseDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.exclude(status='Archived')
    serializer_class = CourseSerializer
    lookup_field = 'course_code'


class ValidCourseList(generics.ListCreateAPIView):
    queryset = Course.objects.exclude(status__in=['Archived', 'Closed'])
    serializer_class = CourseSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ['course_category']
    search_fields = ['course_code', 'course_name', 'status']
    ordering_fields = '__all__'
    ordering = 'course_code'

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)