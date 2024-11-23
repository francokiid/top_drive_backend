from rest_framework.views import APIView
from rest_framework.response import Response
from django_pandas.io import read_frame
from django.db.models import Q
from datetime import datetime
from ....models import Enrollment


class EnrollmentTrends(APIView):
    def get(self, request):
        # FILTER PARAMETERS
        branch = request.query_params.get('branch', None)
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)

        # SET DEFAULT DATE RANGE IF NOT PROVIDED
        if not start_date:
            start_date = datetime(datetime.now().year, 1, 1).date()
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()

        # FETCH DATA FROM DATABASE
        enrollments = Enrollment.objects.exclude(status__in=['Archived', 'Cancelled'])

        # FILTER ENROLLMENTS BASED ON BRANCH AND DATE RANGE
        if branch:
            enrollments = enrollments.filter(branch=branch)
        enrollments = enrollments.filter(Q(session__session_date__gte=start_date))
        if end_date:
            enrollments = enrollments.filter(Q(session__session_date__lte=end_date))

        enrollments = enrollments.distinct()

        # CONVERT DATA TO DATAFRAME
        df_enrollments = read_frame(enrollments, fieldnames=['course', 'course__course_category', 'branch'])

        # TOTAL ENROLLMENTS FOR PERCENTAGE CALCULATION
        total_enrollments = df_enrollments.shape[0]

        if total_enrollments == 0:
            return Response({
                'courseStats': [],
                'courseCategoryStats': [],
                'branchStats': []
            })

        # COURSE CATEGORY STATS
        course_category_stats = (
            df_enrollments.groupby('course__course_category')
            .size().reset_index(name='count')
            .rename(columns={'course__course_category': 'name'})
        )
        course_category_stats['percentage'] = (course_category_stats['count'] / total_enrollments * 100).astype(int)
        course_category_stats = course_category_stats[['name', 'count', 'percentage']].to_dict(orient='records')

        # COURSE STATS
        course_stats = {
            course_category: (
                group['course']
                .value_counts().reset_index(name='count')
                .rename(columns={'course': 'name'}))
            for course_category, group in df_enrollments.groupby('course__course_category')}
        for course_category, stats in course_stats.items():
            stats['percentage'] = (stats['count'] / total_enrollments * 100).astype(int)
            stats['percentage'] = stats['percentage'].fillna(0)
            course_stats[course_category] = stats[['name', 'count', 'percentage']].to_dict(orient='records')

        # BRANCH STATS
        branch_stats = (
            df_enrollments.groupby('branch')
            .size().reset_index(name='count')
            .rename(columns={'branch': 'name'})
        )
        branch_stats['percentage'] = (branch_stats['count'] / total_enrollments * 100).astype(int)
        branch_stats = branch_stats[['name', 'count', 'percentage']].to_dict(orient='records')

        return Response({
            'courseStats': course_stats,
            'courseCategoryStats': course_category_stats,
            'branchStats': branch_stats
        })
