from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
import django_filters
from rest_framework import filters
from ..models import Enrollment, Student
from ..serializers import EnrollmentSerializer
from ..pagination import LargeResultsSetPagination


class EnrollmentFilter(django_filters.FilterSet):
    course_category_type = django_filters.CharFilter(field_name='course__course_category__category_type')
    branch = django_filters.CharFilter('branch__branch_name')

    class Meta:
        model = Enrollment
        fields = ['status', 'course_category_type', 'branch']

class EnrollmentList(generics.ListCreateAPIView):
    queryset = Enrollment.objects.exclude(status='Archived')
    serializer_class = EnrollmentSerializer
    pagination_class = LargeResultsSetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = EnrollmentFilter
    search_fields = ['enrollment_id', 'status']
    ordering_fields = '__all__'
    ordering = 'enrollment_date'

class EnrollmentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Enrollment.objects.exclude(status='Archived')
    serializer_class = EnrollmentSerializer
    lookup_field = 'enrollment_id'

class StudentEnrollmentList(generics.ListAPIView):
    serializer_class = EnrollmentSerializer

    def get_queryset(self):
        student_code = self.kwargs['student_code']
        student = Student.objects.get(pk = student_code)
        return Enrollment.objects.filter(student = student).exclude(status='Archived')