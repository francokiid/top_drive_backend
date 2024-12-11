from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.db import transaction
from django.db.models import Max
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from datetime import datetime
from ..pagination import StandardResultsSetPagination
from ..models import Student, User, Course, Branch, Enrollment
from ..serializers import StudentSerializer, UserSerializer
import django_filters


class StudentFilter(django_filters.FilterSet):
    branch = django_filters.CharFilter('enrollment__branch__branch_name')

    class Meta:
        model = Student
        fields = ['status', 'branch']


class StudentList(generics.ListCreateAPIView):
    queryset = Student.objects.exclude(status='Archived').annotate(
        enrollment_date=Max('enrollment__enrollment_date')
    )
    serializer_class = StudentSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_class = StudentFilter
    search_fields = ['student_code', 'first_name', 'last_name', 'year_joined']
    ordering_fields = '__all__'
    ordering = '-enrollment_date'

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class StudentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.exclude(status='Archived')
    serializer_class = StudentSerializer
    lookup_field = 'student_code'
    

class StudentEnrollments(APIView):
    def get(self, request, identifier, *args, **kwargs):
        try:
            if '@' in identifier:
                user = User.objects.get(email=identifier)
                student = user.student
            else:
                student = Student.objects.get(student_code=identifier)

            if not student:
                return Response({'error': 'Student not found'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = StudentSerializer(student)

            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)
        

class EnrollStudent(APIView):
    def post(self, request, format=None):
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        address = request.data.get('address', '')
        contact_number = request.data.get('contact_number', '')
        emergency_number = request.data.get('emergency_number', '')
        branch_id = request.data.get('branch')
        course_id = request.data.get('course')
        transmission_type = request.data.get('transmission_type')
        total_hours = request.data.get('total_hours')
        preferred_dates = request.data.get('preferred_dates', [])
        remarks = request.data.get('remarks', '')

        if not all([first_name, last_name, branch_id, course_id, transmission_type, total_hours]):
            return Response({'error': "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            total_hours = int(total_hours)
        except ValueError:
            return Response({'error': 'Total hours must be a valid integer.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                student = Student(
                    first_name=first_name,
                    last_name=last_name,
                    address=address,
                    contact_number=contact_number,
                    emergency_number=emergency_number,
                    year_joined=datetime.now().year,
                    status='Active'
                )
                student.save()

                branch = Branch.objects.get(pk=branch_id)
                course = Course.objects.get(pk=course_id)

                enrollment = Enrollment(
                    branch=branch,
                    student=student,
                    course=course,
                    transmission_type=transmission_type,
                    total_hours=total_hours,
                    preferred_dates=preferred_dates,
                    remarks=remarks,
                )
                enrollment.save()

            return Response({'message': 'Student and enrollment registered successfully.'}, status=status.HTTP_201_CREATED)

        except (Branch.DoesNotExist, Course.DoesNotExist) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'Error enrolling student: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)