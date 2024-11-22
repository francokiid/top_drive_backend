from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from math import ceil
from ....models import Enrollment
from . import instructor_recommendation, vehicle_recommendation, classroom_recommendation

class ScheduleRecommendation(APIView):
    def get(self, request):
        # EXTRACT AND VALIDATE REQUEST DATA
        required_fields = ['session_nth', 'session_date', 'start_time', 'end_time']
        missing_fields = [field for field in required_fields if field not in request.GET]
        if missing_fields:
            return Response({field: f"{field} is required." for field in missing_fields}, status=status.HTTP_400_BAD_REQUEST)

        enrollment_id = request.GET.get('enrollment_id', "")
        session_nth = int(request.GET.get('session_nth', 1))
        session_date = request.GET.get('session_date', "")
        start_time = request.GET.get('start_time', "")
        end_time = request.GET.get('end_time', "")
        branch = request.GET.get('branch', "")

        if not enrollment_id:
            return Response({
                "vehicles": [],
                "classrooms": [],
                "instructors": []
            }, status=status.HTTP_200_OK)

        try:
            # FETCH ENROLLMENT DATA
            enrollment = Enrollment.objects.select_related('branch', 'course', 'course__course_category').get(pk=enrollment_id)
            wheel_num = enrollment.course.course_category.category_code
            transmission_type = enrollment.transmission_type
            branch = branch or enrollment.branch
            total_hours = enrollment.total_hours
            last_session = ceil(total_hours / 2)
            category = enrollment.course.course_category.category_type

            # DECIDE RECOMMENDATION BASED ON COURSE CATEGORY
            if category == 'PDC':
                # RECOMMEND VEHICLES AND INSTRUCTORS
                recommended_vehicles = vehicle_recommendation.get_recommended_vehicles(
                    wheel_num, transmission_type, session_date, start_time, end_time, branch
                )
                recommended_instructors = instructor_recommendation.get_recommended_instructors(
                    category, session_date, start_time, end_time, branch, session_nth, last_session
                )
                return Response({
                    "vehicles": recommended_vehicles,
                    "instructors": recommended_instructors,
                }, status=status.HTTP_200_OK)

            elif category == 'TDC':
                # RECOMMEND CLASSROOMS AND INSTRUCTORS
                recommended_classrooms = classroom_recommendation.get_recommended_classrooms(
                    wheel_num, transmission_type, session_date, start_time, end_time, branch
                )
                recommended_instructors = instructor_recommendation.get_recommended_instructors(
                    category, session_date, start_time, end_time, branch, session_nth, last_session
                )
                return Response({
                    "classrooms": recommended_classrooms,
                    "instructors": recommended_instructors,
                }, status=status.HTTP_200_OK)

            else:
                return Response({
                    "message": "Invalid course category."
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "vehicles": [],
                "classrooms": [],
                "instructors": []
            }, status=status.HTTP_200_OK)
