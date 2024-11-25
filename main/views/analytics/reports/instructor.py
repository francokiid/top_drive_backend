from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime, timedelta
from ..utils import get_instructor_utilization


class InstructorUtilization(APIView):
    def get(self, request):
        try:
            branch = request.query_params.get('branch')
            start_date_str = request.query_params.get('start_date')
            end_date_str = request.query_params.get('end_date')
            instructor_code = request.query_params.get('instructor')

            # IF NOT SET, DEFAULT TO CURRENT MONTH
            if not start_date_str:
                start_date = datetime(datetime.now().year, datetime.now().month, 1).date()
            else:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()

            if not end_date_str:
                today = datetime.now().date()
                first_day_next_month = (today.replace(day=1) + timedelta(days=32)).replace(day=1)
                end_date = (first_day_next_month - timedelta(days=1))
            else:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

            data = get_instructor_utilization(branch, start_date, end_date, instructor_code)
            return Response(data, status=status.HTTP_200_OK)

        except ValueError:
            return Response({"error": "Invalid date format. Please use yyyy-mm-dd."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
