from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django_pandas.io import read_frame
from django.contrib.contenttypes.models import ContentType
from datetime import date
from ....models import Session, Classroom, Facility
import json


class TdcScheduleList(APIView):
    def get(self, request, *args, **kwargs):
        try:
            params = self.validate_and_extract_params(request.query_params)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # FETCH SESSIONS
        sessions = self.fetch_sessions(params)

        # PREPARE SCHEDULE RECOMMENDATIONS
        recommendations = self.prepare_recommendations(sessions, params['preferred_dates'])
        return Response(recommendations, status=status.HTTP_200_OK)

    def validate_and_extract_params(self, query_params):
        branch = query_params.get('branch')
        session_nth = query_params.get('session_nth')
        preferred_dates = query_params.get('preferred_dates')

        if not branch:
            raise ValueError("Branch parameter is required.")

        preferred_dates_list = []
        if preferred_dates:
            try:
                preferred_dates_list = json.loads(preferred_dates)
                preferred_dates_list = [date.fromisoformat(d) for d in preferred_dates_list]
            except (json.JSONDecodeError, ValueError):
                raise ValueError("Invalid preferred_dates format. Use JSON array of ISO-formatted dates.")

        return {
            "branch": branch,
            "session_nth": session_nth,
            "preferred_dates": preferred_dates_list,
        }

    def fetch_sessions(self, params):
        return Session.objects.filter(
            facility__facility_type='Classroom',
            session_nth=params['session_nth'],
            status='Scheduled',
            session_date__gte=date.today(),
            enrollment__branch__branch_name=params['branch']
        ).select_related('facility', 'instructor')

    def prepare_recommendations(self, sessions, preferred_dates):
        df = read_frame(
            sessions,
            fieldnames=['session_date', 'facility__object_id', 'instructor__first_name', 'instructor__instructor_code', 'start_time', 'end_time']
        )

        # ADD CAPACITY, FACILITY ID, AND DURATION COLUMNS
        capacity_info = df['facility__object_id'].apply(self.get_capacity)
        df['capacity'] = capacity_info.apply(lambda x: x['capacity'])
        df['facilityId'] = capacity_info.apply(lambda x: x['facilityId'])
        df['duration'] = df.apply(lambda row: f"{row['start_time']} to {row['end_time']}", axis=1)

        # RENAME COLUMNS
        df.rename(columns={'session_date' : 'sessionDate', 'facility__object_id': 'classroom', 'instructor__first_name': 'instructor', 'instructor__instructor_code': 'instructorCode', 'start_time': 'startTime', 'end_time': 'endTime'}, inplace=True)
        aggregated = (
            df.groupby(['sessionDate', 'classroom', 'instructor', 'instructorCode', 'capacity', 'startTime', 'endTime', 'facilityId'])
            .size()
            .reset_index(name='scheduled')
        )

        # CREAYE AVAILABLE SLOTS AND PREFERRED DATE COLUMNS
        aggregated['availableSlots'] = aggregated['capacity'] - aggregated['scheduled']
        aggregated['isPreferred'] = aggregated['sessionDate'].apply(lambda x: x in preferred_dates)

        # FILTER AND SORT RECOMMENDATIONS
        filtered = aggregated[aggregated['availableSlots'] > 0]
        return filtered.sort_values(
            by=['isPreferred', 'availableSlots', 'sessionDate', 'startTime', 'endTime'],
            ascending=[False, False, False, True, True]
        ).to_dict(orient='records')


    def get_capacity(self, facility_code):
        try:
            # RETRIEVE CLASSROOM INSTANCE THAT MATCHES CLASSROOM CODE
            classroom = Classroom.objects.get(classroom_code=facility_code)
            return {
                "capacity": classroom.capacity,
                "facilityId": Facility.objects.get(
                    content_type=ContentType.objects.get_for_model(Classroom),
                    object_id=facility_code
                ).id
            }
        except (Classroom.DoesNotExist, Facility.DoesNotExist):
            return {"capacity": None, "facilityId": None}

