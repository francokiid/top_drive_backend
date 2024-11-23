from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from ..pagination import StandardResultsSetPagination
from ..models import Student, User, Course, Branch, Enrollment
from ..serializers import StudentSerializer, UserSerializer
import django_filters


class EnrollmentFilter(django_filters.FilterSet):
    branch = django_filters.CharFilter('enrollment__branch__branch_name')

    class Meta:
        model = Student
        fields = ['status', 'branch']

class StudentList(generics.ListCreateAPIView):
    queryset = Student.objects.exclude(status='Archived')
    serializer_class = StudentSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_class = EnrollmentFilter
    search_fields = ['student_code', 'first_name', 'last_name', 'year_joined']
    ordering_fields = '__all__'
    ordering = 'student_code'

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class StudentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.exclude(status='Archived')
    serializer_class = StudentSerializer
    lookup_field = 'student_code'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        user_data = {
            'email': request.data.get('email'),
            'password': request.data.get('password'),
            're_password': request.data.get('re_password'),
            'first_name': request.data.get('first_name'),
            'last_name': request.data.get('last_name')
        }

        email = user_data.get('email')
        password = user_data.get('password')
        re_password = user_data.get('re_password')

        if email:
            try:
                user = User.objects.get(email=email)
                if password and re_password:
                    if password != re_password:
                        return Response({'error': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)
                    if len(password) < 6:
                        return Response({'error': 'Password must be at least 6 characters.'}, status=status.HTTP_400_BAD_REQUEST)
                    user.set_password(password)
                user.first_name = user_data.get('first_name', user.first_name)
                user.last_name = user_data.get('last_name', user.last_name)
                user.save()

            except User.DoesNotExist:
                if not password or not re_password:
                    return Response({'error': 'Password and re_password are required for a new user.'}, status=status.HTTP_400_BAD_REQUEST)
                if password != re_password:
                    return Response({'error': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)
                if len(password) < 6:
                    return Response({'error': 'Password must be at least 6 characters.'}, status=status.HTTP_400_BAD_REQUEST)

                user = User.objects.create_user(
                    email=email,
                    password=password,
                    first_name=user_data.get('first_name'),
                    last_name=user_data.get('last_name')
                )

            instance.user = user
            instance.save()

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class EnrollStudent(APIView):
    def post(self, request, format=None):
        branch_id = request.data.get('branch')
        course_id = request.data.get('course')
        transmission_type = request.data.get('transmission_type')
        total_hours = request.data.get('total_hours')
        preferred_dates = request.data.get('preferred_dates', [])
        remarks = request.data.get('remarks', '')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name', '')

        if not all([branch_id, course_id, transmission_type, total_hours, first_name]):
            return Response({'error': "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            total_hours = int(total_hours)
        except ValueError:
            return Response({'error': 'Total hours must be a valid integer.'}, status=status.HTTP_400_BAD_REQUEST)

        user_data = {
            'email': request.data.get('email'),
            'password': request.data.get('password'),
            're_password': request.data.get('re_password'),
            'first_name': first_name,
            'last_name': last_name
        }

        try:
            with transaction.atomic():
                student = Student(first_name=first_name, last_name=last_name)

                if user_data['email'] and user_data['password']:
                    user_serializer = UserSerializer(data=user_data)
                    if user_serializer.is_valid(raise_exception=True):
                        user = user_serializer.save()
                        student.user = user
                
                student.save()

                branch = Branch.objects.get(pk=branch_id)
                course = Course.objects.get(pk=course_id)

                enrollment = Enrollment(
                    branch=branch,
                    student=student,
                    course=course,
                    transmission_type=transmission_type,
                    total_hours=total_hours,
                    remarks=remarks,
                    preferred_dates=preferred_dates,
                )
                enrollment.save()

            return Response({'message': 'Student and enrollment registered successfully.'}, status=status.HTTP_201_CREATED)

        except (Branch.DoesNotExist, Course.DoesNotExist) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'Error enrolling student: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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

