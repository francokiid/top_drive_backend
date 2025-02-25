from django_pandas.io import read_frame
import pandas as pd
from ....models import Session, Instructor
from . import calculate_date_range


def get_instructor_utilization(branch=None, start_date=None, end_date=None, instructor_code=None):
    # GET DATE RANGE AND DEFAULT TO CURRENT WEEK IF NO DATES ARE PROVIDED
    start_date, end_date = calculate_date_range(start_date, end_date)

    # FETCH INSTRUCTORS WITH BRANCH NAME AND FILTER BY INSTRUCTOR CODE IF PROVIDED
    instructors = Instructor.objects.exclude(status__in=['Archived', 'Inactive', 'On Leave'])

    if branch:
        instructors = instructors.filter(branch=branch)
    if instructor_code:
        instructors = instructors.filter(instructor_code=instructor_code)

    instructors = instructors.values('instructor_code', 'first_name', 'is_senior', 'branch__branch_name')

    if not instructors:
        instructors = Instructor.objects.exclude(status__in=['Archived', 'Inactive']).filter(branch__branch_name="Main").values(
            'instructor_code', 'first_name', 'is_senior', 'branch__branch_name'
        )

    # FETCH SESSIONS BY BRANCH
    sessions_query = Session.objects.filter(session_date__range=[start_date, end_date], status__in=['Completed', 'Scheduled'])
    if branch:
        sessions_query = sessions_query.filter(enrollment__branch=branch)

    # CONVERT DATA TO DF
    df_instructors = read_frame(instructors)
    df_sessions = read_frame(sessions_query.values(
        'instructor_id', 'start_time', 'end_time', 'session_date', 
        'enrollment__course__course_category__category_type'
    ))

    if not df_sessions.empty:
        # FORMAT START AND END TIME
        df_sessions['start_datetime'] = pd.to_datetime(df_sessions['session_date'].astype(str) + ' ' + df_sessions['start_time'].astype(str))
        df_sessions['end_datetime'] = pd.to_datetime(df_sessions['session_date'].astype(str) + ' ' + df_sessions['end_time'].astype(str))

        # SORT AND GROUP SESSIONS BY INSTRUCTOR
        df_sessions = df_sessions.sort_values(by=['instructor_id', 'start_datetime'])
        grouped_sessions = df_sessions.groupby('instructor_id')

        # HANDLE OVERLAPPING SESSIONS
        adjusted_durations = []
        for instructor_id, group in grouped_sessions:
            group = group.sort_values('start_datetime')
            total_duration = 0
            current_start = None
            current_end = None

            for _, session in group.iterrows():
                if current_start is None:
                    # Start tracking a new time range
                    current_start = session['start_datetime']
                    current_end = session['end_datetime']
                elif session['start_datetime'] <= current_end:
                    # Overlapping session, extend the current range
                    current_end = max(current_end, session['end_datetime'])
                else:
                    # No overlap, finalize the previous range
                    total_duration += (current_end - current_start).total_seconds() / 3600  # Convert to hours
                    current_start = session['start_datetime']
                    current_end = session['end_datetime']

            # Finalize the last range
            if current_start and current_end:
                total_duration += (current_end - current_start).total_seconds() / 3600

            adjusted_durations.append({'instructor_id': instructor_id, 'hoursAssigned': total_duration})

        utilization = pd.DataFrame(adjusted_durations)
    else:
        utilization = pd.DataFrame(columns=['instructor_id', 'hoursAssigned'])

    # MERGE INSTRUCTOR DATA WITH UTILIZATION
    utilization = pd.merge(df_instructors, utilization, left_on='instructor_code', right_on='instructor_id', how='left')
    utilization['hoursAssigned'] = utilization['hoursAssigned'].fillna(0).infer_objects(copy=False)

    # CALCULATE HOURS AVAILABLE
    total_days = (end_date - start_date).days + 1
    total_weeks = total_days // 7
    working_days = total_days - total_weeks
    hours_available_per_instructor = working_days * 8
    utilization['hoursAvailable'] = hours_available_per_instructor

    # CALCULATE UTILIZATION RATE
    utilization['utilizationRate'] = (utilization['hoursAssigned'] / utilization['hoursAvailable'] * 100).round(2)

    # SORT INSTRUCTORS BY UTILIZATION RATE
    utilization = utilization.sort_values(by='utilizationRate', ascending=True)

    # CALCULATE OVERALL UTILIZATION
    total_hours_assigned = utilization['hoursAssigned'].sum()
    total_hours_available = len(df_instructors) * hours_available_per_instructor
    overall_utilization_rate = (total_hours_assigned / total_hours_available * 100).round(2)

    # PREPARE RESPONSE
    utilization_data = utilization[['instructor_code', 'first_name', 'is_senior', 'branch__branch_name', 'hoursAvailable', 'hoursAssigned', 'utilizationRate']]
    utilization_data.loc[:, 'instructorName'] = utilization_data.apply(
        lambda row: f"{row['first_name']} SR / {row['branch__branch_name']}" if row['is_senior'] else f"{row['first_name']} / {row['branch__branch_name']}",
        axis=1
    )
    utilization_data = utilization_data.drop(columns=['first_name', 'is_senior', 'branch__branch_name'])
    utilization_data = utilization_data.rename(columns={'instructor_code': 'instructorCode'}).to_dict(orient='records')

    return {
        "overallUtilizationRate": overall_utilization_rate,
        "totalHoursAssigned": total_hours_assigned,
        "totalHoursAvailable": total_hours_available,
        "instructors": utilization_data
    }


# def get_instructor_utilization(branch=None, start_date=None, end_date=None, instructor_code=None):
#     # GET DATE RANGE AND DEFAULT TO CURRENT WEEK IF NO DATES ARE PROVIDED
#     start_date, end_date = calculate_date_range(start_date, end_date)

#     # FETCH INSTRUCTORS WITH BRANCH NAME AND FILTER BY INSTRUCTOR CODE IF PROVIDED
#     instructors = Instructor.objects.exclude(status__in=['Archived', 'Inactive', 'On Leave'])

#     if branch:
#         instructors = instructors.filter(branch=branch)
#     if instructor_code:
#         instructors = instructors.filter(instructor_code=instructor_code)  # Filter by instructor_code if provided

#     instructors = instructors.values('instructor_code', 'first_name', 'is_senior', 'branch__branch_name')

#     if not instructors:
#         instructors = Instructor.objects.exclude(status__in=['Archived', 'Inactive']).filter(branch__branch_name="Main").values(
#             'instructor_code', 'first_name', 'is_senior', 'branch__branch_name'
#         )

#     # FETCH SESSIONS BY BRANCH
#     sessions_query = Session.objects.filter(session_date__range=[start_date, end_date], status__in=['Completed', 'Scheduled'])
#     if branch:
#         sessions_query = sessions_query.filter(enrollment__branch=branch)

#     # CONVERT DATA TO DF
#     df_instructors = read_frame(instructors)
#     df_sessions = read_frame(sessions_query.values(
#         'instructor_id', 'start_time', 'end_time', 'session_date', 
#         'enrollment__course__course_category__category_type'
#     ))

#     if not df_sessions.empty:
#         # FORMAT START AND END TIME
#         df_sessions['start_datetime'] = pd.to_datetime(df_sessions['session_date'].astype(str) + ' ' + df_sessions['start_time'].astype(str))
#         df_sessions['end_datetime'] = pd.to_datetime(df_sessions['session_date'].astype(str) + ' ' + df_sessions['end_time'].astype(str))

#         # SET SESSION DURATION
#         df_sessions['duration'] = df_sessions['enrollment__course__course_category__category_type'].map(
#             {'PDC': 2.0, 'TDC': 7.5}
#         ).fillna(0)

#         # AGGREGATE SESSION DURATION
#         utilization = df_sessions.groupby('instructor_id')['duration'].sum().reset_index()
#         utilization.columns = ['instructor_id', 'hoursAssigned']
#     else:
#         utilization = pd.DataFrame(columns=['instructor_id', 'hoursAssigned'])

#     # MERGE INSTRUCTOR DATA WITH UTILIZATION
#     utilization = pd.merge(df_instructors, utilization, left_on='instructor_code', right_on='instructor_id', how='left')
#     utilization['hoursAssigned'] = utilization['hoursAssigned'].fillna(0).infer_objects(copy=False)

#     # CALCULATE HOURS AVAILABLE
#     total_days = (end_date - start_date).days + 1
#     total_weeks = total_days // 7
#     working_days = total_days - total_weeks
#     hours_available_per_instructor = working_days * 8
#     utilization['hoursAvailable'] = hours_available_per_instructor

#     # CALCULATE UTILIZATION RATE
#     utilization['utilizationRate'] = (utilization['hoursAssigned'] / utilization['hoursAvailable'] * 100).round(2)

#     # SORT INSTRUCTORS BY UTILIZATION RATE
#     utilization = utilization.sort_values(by='utilizationRate', ascending=True)

#     # CALCULATE OVERALL UTILIZATION
#     total_hours_assigned = utilization['hoursAssigned'].sum()
#     total_hours_available = len(df_instructors) * hours_available_per_instructor
#     overall_utilization_rate = (total_hours_assigned / total_hours_available * 100).round(2)

#     # PREPARE RESPONSE
#     utilization_data = utilization[['instructor_code', 'first_name', 'is_senior', 'branch__branch_name', 'hoursAvailable', 'hoursAssigned', 'utilizationRate']]
#     utilization_data.loc[:, 'instructorName'] = utilization_data.apply(
#         lambda row: f"{row['first_name']} SR / {row['branch__branch_name']}" if row['is_senior'] else f"{row['first_name']} / {row['branch__branch_name']}",
#         axis=1
#     )
#     utilization_data = utilization_data.drop(columns=['first_name', 'is_senior', 'branch__branch_name'])
#     utilization_data = utilization_data.rename(columns={'instructor_code': 'instructorCode'}).to_dict(orient='records')

#     return {
#         "overallUtilizationRate": overall_utilization_rate,
#         "totalHoursAssigned": total_hours_assigned,
#         "totalHoursAvailable": total_hours_available,
#         "instructors": utilization_data
#     }