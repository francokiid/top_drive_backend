from rest_framework import generics
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Q
from datetime import datetime
from ..pagination import LargeResultsSetPagination
from ..models import Session, Vehicle, Classroom, Student, Enrollment
from ..serializers import SessionSerializer


class SessionList(generics.ListCreateAPIView):
    queryset = Session.objects.exclude(status='Archived')
    serializer_class = SessionSerializer
    pagination_class = LargeResultsSetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ['status', 'session_date']
    search_fields = ['session_id', 'session_nth', 'session_date', 'status', 
                     'enrollment__course__course_name', 'enrollment__student__student_code', 'enrollment__student__first_name',
                     'instructor__instructor_code', 'instructor__first_name', 'facility__object_id'
                    ]
    ordering_fields = '__all__'
    ordering = 'session_date'

    def get_queryset(self):
        queryset = Session.objects.exclude(status='Archived')

        month = self.request.query_params.get('month', None)
        year = self.request.query_params.get('year', None)
        branch = self.request.query_params.get('branch', None)
        
        if month and year and branch:
            try:
                queryset = queryset.filter(
                    session_date__year=year, 
                    session_date__month=month, 
                    enrollment__branch=branch
                )
            except ValueError:
                pass
        elif month and year:
            try:
                queryset = queryset.filter(session_date__year=year, session_date__month=month)
            except ValueError:
                pass
        elif branch:
            try:
                queryset = queryset.filter(enrollment__branch=branch)
            except ValueError:
                pass

        facility_name = self.request.query_params.get('facility', None)
        
        if facility_name:
            vehicle_ids = Vehicle.objects.filter(name__icontains=facility_name).values_list('id', flat=True)
            classroom_ids = Classroom.objects.filter(name__icontains=facility_name).values_list('id', flat=True)
            queryset = queryset.filter(
                Q(facility__object_id__in=vehicle_ids) | Q(facility__object_id__in=classroom_ids)
            )
        return queryset

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class SessionDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Session.objects.exclude(status='Archived')
    serializer_class = SessionSerializer
    lookup_field = 'session_id'


class StudentSessions(generics.ListAPIView):
    serializer_class = SessionSerializer

    def get_queryset(self):
        student_code = self.kwargs.get('student_code')
        
        student = Student.objects.filter(student_code=student_code).first()
        
        if not student:
            return Session.objects.none()
        
        enrollments = Enrollment.objects.filter(student=student).exclude(status='Archived')
        
        return Session.objects.filter(enrollment__in=enrollments).exclude(status='Archived').select_related('enrollment', 'enrollment__course').prefetch_related('facility')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        grouped_sessions = {}
        for session in queryset:
            enrollment_id = session.enrollment.enrollment_id
            if enrollment_id not in grouped_sessions:
                grouped_sessions[enrollment_id] = []
            grouped_sessions[enrollment_id].append(session)

        serialized_data = self.serialize_grouped_sessions(grouped_sessions)

        return Response(serialized_data)

    def serialize_grouped_sessions(self, grouped_sessions):
        serialized_data = []
        for enrollment_id, sessions in grouped_sessions.items():
            serialized_sessions = SessionSerializer(sessions, many=True).data
            enrollment_data = {
                'enrollment_id': enrollment_id,
                'sessions': serialized_sessions
            }
            serialized_data.append(enrollment_data)
        return serialized_data