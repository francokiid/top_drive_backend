from datetime import datetime
from django.contrib import auth
from django.contrib.auth import authenticate
from django.forms import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from ..models import Student, User, Instructor
from ..serializers import UserSerializer
from ..pagination import StandardResultsSetPagination


class UserList(generics.ListCreateAPIView):
    serializer_class = UserSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ['role']
    search_fields = ['role', 'email', 'first_name', 'last_name', 'branch__branch_name']
    ordering_fields = '__all__'
    ordering = 'role'

    def get_queryset(self):
        condition = self.request.query_params.get('condition', 'all')
        role = self.request.query_params.get('role', None)

        queryset = User.objects.all()

        if condition == 'no_association':
            queryset = queryset.filter(role='Student').exclude(
                student__isnull=False
            ).exclude(
                instructor__isnull=False
            )

        if role:
            queryset = queryset.filter(role=role)

        return queryset

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'email'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)

        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        try:
            instructor = Instructor.objects.get(user=instance)
            if 'first_name' in serializer.validated_data:
                instructor.first_name = serializer.validated_data['first_name']
            if 'last_name' in serializer.validated_data:
                instructor.last_name = serializer.validated_data['last_name']
            instructor.save()
        except Instructor.DoesNotExist:
            pass

        try:
            student = Student.objects.get(user=instance)
            if 'first_name' in serializer.validated_data:
                student.first_name = serializer.validated_data['first_name']
            if 'last_name' in serializer.validated_data:
                student.last_name = serializer.validated_data['last_name']
            student.save()
        except Student.DoesNotExist:
            pass

        return Response(serializer.data, status=status.HTTP_200_OK)

class RegisterView(APIView):
    permission_classes = (permissions.AllowAny, )

    def post(self, request, format=None):
        data = request.data
        email = data.get('email')
        password = data.get('password')
        re_password = data.get('re_password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')

        if not all([email, password, re_password, first_name, last_name]):
            return Response({'error': 'Missing required fields.'}, status=status.HTTP_400_BAD_REQUEST)
        if password != re_password:
            return Response({'error': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)
        if len(password) < 6:
            return Response({'error': 'Password must be at least 6 characters.'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.create_user(email=email, password=password, first_name=first_name, last_name=last_name, role='Student')
            student = Student(
                student_name=f"{first_name} {last_name}",
                user=user,
                year_joined=datetime.now().year,
                status='Active'
            )
            student.save()
            return Response({'message': 'Student registered successfully.'}, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'Error creating account: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = auth.authenticate(request, email=email, password=password)
        if user is not None:
            auth.login(request, user)
            role = user.role
            can_edit = user.can_edit
            is_active = user.is_active
            branch = user.branch.branch_name if user.branch else None
            print(branch)
            return Response({'bool': True, 'email': email, 'role': role, 'can_edit': can_edit, 'is_active': is_active, 'branch': branch}, status=status.HTTP_200_OK)
        else:
            return Response({'bool': False}, status=status.HTTP_401_UNAUTHORIZED)
        
class LogoutView(APIView):
    def post(self, request, format=None):
        try:
            auth.logout(request)
            return Response({'success': 'Logged out'})
        except Exception as e:
            return Response({'error': f'Logout failed. Something went wrong: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ConfirmPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(email=email, password=password)
        
        if user is not None:
            return Response({'success': True}, status=200)
        return Response({'success': False, 'error': 'Invalid password'}, status=400)

class ChangePasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        if not user.check_password(current_password):
            return Response({'error': 'Current password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
        if len(new_password) < 6:
            return Response({'error': 'Password must be at least 6 characters long.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({'message': 'Password updated successfully'}, status=status.HTTP_200_OK)