from rest_framework.views import APIView
from rest_framework.response import Response
from django_pandas.io import read_frame
from ....models import Instructor, Classroom, Vehicle


class ResourceStats(APIView):
    def get(self, request):
        branch = request.query_params.get('branch', None)

        # FILTER RESOURCES BY BRANCH
        instructors = Instructor.objects.exclude(status__in=['Archived', 'Inactive'])
        classrooms = Classroom.objects.filter(status="Available")
        vehicles = Vehicle.objects.filter(status="Available")

        if branch:
            instructors = instructors.filter(branch=branch)
            classrooms = classrooms.filter(branch=branch)
            vehicles = vehicles.filter(branch=branch)

        df_instructors = read_frame(instructors, fieldnames=['instructor_code'])
        df_classrooms = read_frame(classrooms, fieldnames=['classroom_code'])
        df_vehicles = read_frame(vehicles, fieldnames=['vehicle_code'])

        instructor_count = df_instructors.shape[0]
        classroom_count = df_classrooms.shape[0]
        vehicle_count = df_vehicles.shape[0]

        return Response({
            'instructorCount': instructor_count,
            'classroomCount': classroom_count,
            'vehicleCount': vehicle_count
        })
