from rest_framework.views import APIView
from rest_framework.response import Response
from django_pandas.io import read_frame
import pandas as pd
from datetime import datetime
from ....models import Session


class SessionTrends(APIView):
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        branch = request.query_params.get('branch')

        # SET DEFAULT START DATE IF NOT PROVIDED
        if not start_date:
            start_date = datetime(datetime.now().year, 1, 1).date()

        # LOAD DATA INTO A DATAFRAME
        sessions = Session.objects.exclude(status__in=['Archived', 'Cancelled'])
        
        # FILTER SESSIONS BASED ON BRANCH AND DATE RANGE
        sessions = sessions.filter(session_date__gte=start_date)
        if end_date:
            sessions = sessions.filter(session_date__lte=end_date)
        if branch:
            sessions = sessions.filter(enrollment__branch=branch)

        # CONVERT DATA TO DATAFRAME
        df_sessions = read_frame(sessions, fieldnames=['session_date', 'start_time', 'status', 'enrollment__course__course_category'])

        # FORMAT COLUMNS
        df_sessions['session_date'] = pd.to_datetime(df_sessions['session_date'])
        df_sessions['start_time'] = pd.to_datetime(df_sessions['start_time'], format='%H:%M:%S').dt.time

        # COUNT OF UPCOMING SESSIONS
        scheduled_count = df_sessions[df_sessions['status'] == 'Scheduled'].shape[0]

        # TOTAL NUMBER OF SESSIONS FOR PERCENTAGE CALCULATION
        total_sessions = df_sessions.shape[0]

        if total_sessions == 0:
            return Response({
                'monthlyStats': [],
                'dailyStats': {},
                'timeRangeStats': {},
                'timePeriodStats': [],
                'statusStats': [],
                'courseCategoryStats': {},
                'scheduledCount': scheduled_count,
            })

        # MONTHLY STATS
        session_trends = (
            df_sessions.groupby(df_sessions['session_date'].dt.to_period('M'))
            .size()
            .reset_index(name='count'))
        session_trends['month'] = session_trends['session_date'].dt.strftime('%b')
        session_trends['percentage'] = (session_trends['count'] / total_sessions * 100).round(0).astype(int)
        monthly_stats = session_trends[['month', 'count', 'percentage']].to_dict(orient='records')

        # DAILY STATS GROUPED BY MONTH
        df_sessions['day'] = df_sessions['session_date'].dt.strftime('%a')
        day_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        daily_stats = {
            month: group.groupby('day').size().reset_index(name='count').sort_values(by='day', key=lambda x: x.map({day: i for i, day in enumerate(day_order)}))
            for month, group in df_sessions.groupby(df_sessions['session_date'].dt.strftime('%b'))
        }
        for month, stats in daily_stats.items():
            stats['percentage'] = (stats['count'] / total_sessions * 100).round(0).astype(int)
            daily_stats[month] = stats[['day', 'count', 'percentage']].to_dict(orient='records')

        # CATEGORIZE SESSIONS BY TIME PERIOD
        df_sessions['time_period'] = df_sessions['start_time'].apply(self.categorize_time)

        # TIME PERIOD STATS
        time_period_stats = df_sessions.groupby('time_period').size().reset_index(name='count').rename(columns={'time_period': 'name'})
        time_period_stats['percentage'] = (time_period_stats['count'] / total_sessions * 100).round(0).astype(int)
        time_period_stats = time_period_stats[['name', 'count', 'percentage']].to_dict(orient='records')

        # TIME RANGE STATS GROUPED BY TIME PERIOD
        df_sessions['time_range'] = df_sessions.apply(self.combine_time_range, axis=1)
        time_range_stats = {
            time_period: group.groupby('time_range').size().reset_index(name='count').rename(columns={'time_range': 'name'})
            for time_period, group in df_sessions.groupby('time_period')
        }
        for time_period, stats in time_range_stats.items():
            stats['percentage'] = (stats['count'] / total_sessions * 100).round(0).astype(int)
            time_range_stats[time_period] = stats[['name', 'count', 'percentage']].to_dict(orient='records')

        # STATUS STATS
        status_stats = df_sessions.groupby('status').size().reset_index(name='count').rename(columns={'status': 'name'})
        status_stats['percentage'] = (status_stats['count'] / total_sessions * 100).round(0).astype(int)
        status_stats = status_stats[['name', 'count', 'percentage']].to_dict(orient='records')

        # COURSE CATEGORY STATS GROUPED BY STATUS
        course_category_stats = {
            status: df_sessions[df_sessions['status'] == status]
            .groupby('enrollment__course__course_category').size().reset_index(name='count').rename(columns={'enrollment__course__course_category': 'name'})
            for status in df_sessions['status'].unique()
        }
        for status, stats in course_category_stats.items():
            stats['percentage'] = (stats['count'] / total_sessions * 100).astype(int)
            course_category_stats[status] = stats[['name', 'count', 'percentage']].to_dict(orient='records')

        return Response({
            'monthlyStats': monthly_stats,
            'dailyStats': daily_stats,
            'timeRangeStats': time_range_stats,
            'timePeriodStats': time_period_stats,
            'statusStats': status_stats,
            'courseCategoryStats': course_category_stats,
            'scheduledCount': scheduled_count,
        })

    @staticmethod
    def categorize_time(start_time):
        if start_time.hour < 12:
            return 'Morning'
        elif start_time.hour < 17:
            return 'Afternoon'
        return 'Evening'

    @staticmethod
    def combine_time_range(row):
        return row['start_time'].strftime('%I:%M')