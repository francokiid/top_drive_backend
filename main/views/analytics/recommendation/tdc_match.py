from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from .tdc_schedule_list import TdcScheduleList
import json


class TdcScheduleMatch(APIView):
    def get(self, request):
        # EXTRACT AND VALIDATE REQUEST DATA
        required_fields = ['session_nth', 'session_date', 'start_time', 'end_time', 'branch']
        missing_fields = [field for field in required_fields if field not in request.GET]
        if missing_fields:
            return Response(
                {field: f"{field} is required." for field in missing_fields},
                status=status.HTTP_400_BAD_REQUEST
            )

        session_date = request.GET.get('session_date', "")
        session_nth = int(request.GET.get('session_nth', 1))
        start_time = request.GET.get('start_time', "")
        end_time = request.GET.get('end_time', "")
        branch = request.GET.get('branch', "")
        preferred_dates = request.GET.get('preferred_dates')

        # PARSE SESSION DATE
        try:
            session_date = datetime.strptime(session_date, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "Invalid session_date format. Use ISO format (YYYY-MM-DD)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # PARSE START TIME AND END TIME
        try:
            start_time = datetime.strptime(start_time, "%H:%M").time()
            end_time = datetime.strptime(end_time, "%H:%M").time()
        except ValueError:
            return Response(
                {"error": "Invalid time format. Use HH:MM format."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # PARSE PREFERRED DATES
        preferred_dates_list = []
        if preferred_dates:
            try:
                preferred_dates_list = [datetime.strptime(d, "%Y-%m-%d").date() for d in json.loads(preferred_dates)]
            except ValueError:
                return Response(
                    {"error": "Invalid date format in preferred_dates. Use ISO format (YYYY-MM-DD)."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # CALL TdcScheduleRecommendation TO GET RECOMMENDED SCHEDULES
        recommendation_request = {
            'branch': branch,
            'session_nth': session_nth,
            'preferred_dates': None
        }
        recommendation_view = TdcScheduleList()
        recommendation_response = recommendation_view.get(request=type('Request', (object,), {"query_params": recommendation_request}))

        if recommendation_response.status_code != 200:
            return Response(
                {"error": "Failed to fetch recommendations."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        recommended_schedules = recommendation_response.data

        # CHECK IF ANY RECOMMENDED SCHEDULE MATCHES THE PROVIDED DETAILS
        matching_schedules = []
        for schedule in recommended_schedules:
            formatted_session_date = schedule['sessionDate'].strftime('%Y-%m-%d')
            formatted_start_time = schedule['startTime'].strftime('%H:%M:%S')
            formatted_end_time = schedule['endTime'].strftime('%H:%M:%S')

            if formatted_session_date == str(session_date) and formatted_start_time == str(start_time) and formatted_end_time == str(end_time):
                matching_schedules.append(schedule)

        # PREPARE RESPONSE
        response_data = {
            "matches": matching_schedules,
            "hasMatch": bool(matching_schedules)
        }

        return Response(response_data, status=status.HTTP_200_OK)
