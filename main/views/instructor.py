from rest_framework import generics, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from ..pagination import StandardResultsSetPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.exceptions import ValidationError
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from ..models import Instructor, User, Branch, Session
from ..serializers import InstructorSerializer, SessionSerializer


class InstructorList(generics.ListCreateAPIView):
    queryset = Instructor.objects.exclude(status='Archived')
    serializer_class = InstructorSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ['branch']
    search_fields = ['instructor_code', 'first_name', 'last_name', 'status', 'branch__branch_name']
    ordering_fields = '__all__'
    ordering = 'instructor_code'

    def get_queryset(self):
        queryset = Instructor.objects.all()
        date = self.request.query_params.get('date', None)
        start_time = self.request.query_params.get('start_time', None)
        end_time = self.request.query_params.get('end_time', None)

        if date and start_time:
            try:
                start_datetime = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")

                if end_time:
                    end_datetime = datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M")
                else:
                    end_datetime = datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M") if end_time else datetime.strptime(f"{date} 23:59", "%Y-%m-%d %H:%M")

                busy_instructors = Session.objects.filter(
                    session_date=date,
                    start_time__lt=end_datetime,
                    end_time__gt=start_datetime,
                    status__in=['Completed', 'Scheduled']
                ).values_list('instructor__instructor_code', flat=True)

                queryset = queryset.exclude(instructor_code__in=list(busy_instructors))
            except ValueError:
                pass

        return queryset

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class InstructorDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Instructor.objects.exclude(status='Archived')
    serializer_class = InstructorSerializer
    lookup_field = 'instructor_code'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        first_name = request.data.get('first_name', instance.first_name)
        last_name = request.data.get('last_name', instance.last_name)
        is_senior = request.data.get('is_senior', instance.is_senior)
        branch_name = request.data.get('branch_name', instance.branch.branch_name)
        ins_status = request.data.get('status', instance.status)

        if not all([first_name, is_senior is not None, branch_name, ins_status]):
            return Response({'error': 'Missing required fields.'}, status=status.HTTP_400_BAD_REQUEST)

        email = request.data.get('email')
        password = request.data.get('password')
        re_password = request.data.get('re_password')

        user = instance.user if instance.user else None

        if email or password: 
            if password and password != re_password:
                return Response({'error': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)
            if password and len(password) < 6:
                return Response({'error': 'Password must be at least 6 characters.'}, status=status.HTTP_400_BAD_REQUEST)

            if user is None:
                if email:
                    user = User.objects.create_user(
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                        role='Instructor'
                    )
                else:
                    return Response({'error': 'Email must be provided when creating a user.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                if email and email != user.email:
                    if User.objects.filter(email=email).exists():
                        return Response({'error': 'Email already exists.'}, status=status.HTTP_400_BAD_REQUEST)
                    user.email = email

                if password:
                    user.set_password(password)
                user.first_name = first_name
                user.last_name = last_name
                user.save()

            instance.user = user

        try:
            branch = Branch.objects.get(branch_name=branch_name)
        except Branch.DoesNotExist:
            return Response({'error': 'Branch does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        instance.first_name = first_name
        instance.last_name = last_name
        instance.is_senior = is_senior
        instance.branch = branch
        instance.status = ins_status
        instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class CreateInstructor(APIView):
    def post(self, request, format=None):
        data = request.data
        first_name = data.get('first_name')
        last_name = data.get('last_name', '')
        is_senior = data.get('is_senior')
        is_senior = str(is_senior).lower() == 'true'
        branch_name = data.get('branch_name')
        ins_status = data.get('status')
        email = data.get('email', '')
        password = data.get('password', '')
        re_password = data.get('re_password', '')

        if not all([first_name, is_senior is not None, branch_name, ins_status]):
            return Response({'error': 'Missing required fields.'}, status=status.HTTP_400_BAD_REQUEST)

        if email:
            if password != re_password:
                return Response({'error': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)
            if len(password) < 6:
                return Response({'error': 'Password must be at least 6 characters.'}, status=status.HTTP_400_BAD_REQUEST)

            if User.objects.filter(email=email).exists():
                return Response({'error': 'Email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = User.objects.create_user(
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    role='Instructor'
                )
            except ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user = None

        try:
            branch = Branch.objects.get(branch_name=branch_name)
        except Branch.DoesNotExist:
            return Response({'error': 'Branch does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            instructor = Instructor(
                first_name=first_name,
                last_name=last_name,
                is_senior=is_senior,
                branch=branch,
                status=ins_status,
                user=user
            )
            instructor.save()

            return Response({
                'message': 'Instructor added successfully.',
                'instructor': InstructorSerializer(instructor).data
            }, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'Error creating instructor: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InstructorSessions(APIView):
    def get(self, request, *args, **kwargs):
        email = self.kwargs.get('email')
        
        try:
            instructor = Instructor.objects.get(user__email=email)
            sessions = Session.objects.filter(instructor=instructor)

            remaining_sessions_today_count = sessions.filter(
                status='Scheduled',
                session_date=datetime.now()
            ).count()

            upcoming_sessions_count = sessions.filter(
                status='Scheduled',
                session_date__gt=datetime.now()
            ).count()

            instructor_data = InstructorSerializer(instructor).data
            sessions_data = SessionSerializer(sessions, many=True).data

            response_data = {**instructor_data, 'sessions': sessions_data, 'upcoming_sessions': upcoming_sessions_count, 'remaining_sessions': remaining_sessions_today_count}

            return Response(response_data, status=status.HTTP_200_OK)

        except Instructor.DoesNotExist:
            return Response({'error': 'Instructor with this email does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        except ObjectDoesNotExist:
            return Response({'error': 'Error retrieving data.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
