from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime
from ..utils import get_classroom_utilization


class ClassroomUtilization(APIView):
  def get(self, request):
    try:
      branch = request.query_params.get('branch')
      start_date_str = request.query_params.get('start_date')
      end_date_str = request.query_params.get('end_date')

      start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
      end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None

      data = get_classroom_utilization(branch, start_date, end_date)
      return Response(data, status=status.HTTP_200_OK)

    except ValueError:
      return Response({"error": "Invalid date format. Please use yyyy-mm-dd."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
      return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
