from django_pandas.io import read_frame
import pandas as pd
from ....models import Session, Classroom
from . import calculate_date_range, calculate_utilization


def get_classroom_utilization(branch=None, start_date=None, end_date=None):
    # GET DATE RANGE AND DEFAULT TO CURRENT WEEK IF NO DATES ARE PROVIDED
    start_date, end_date = calculate_date_range(start_date, end_date)

    # FETCH CLASSROOMS WITH BRANCH NAME
    if branch:
        classrooms = Classroom.objects.exclude(status__in=['Archived', 'Unavailable']).filter(branch=branch).values(
            'classroom_code', 'capacity', 'branch__branch_name'
        )
        if not classrooms:
            classrooms = Classroom.objects.exclude(status__in=['Archived', 'Unavailable']).filter(branch='Main').values(
                'classroom_code', 'capacity', 'branch__branch_name'
            )
    else:
        classrooms = Classroom.objects.exclude(status__in=['Archived', 'Unavailable']).values(
            'classroom_code', 'capacity', 'branch__branch_name'
        )

    # FETCH SESSIONS AND FILTER BY BRANCH AND DATE RANGE
    sessions = Session.objects.exclude(status__in=['Archived', 'Unavailable']).filter(session_date__range=[start_date, end_date])
    if branch:
        sessions = sessions.filter(enrollment__branch=branch)
    
    # CONVERT CLASSROOMS TO DATAFRAME
    df_facilities = read_frame(classrooms)
    df_facilities = df_facilities.rename(columns={'classroom_code': 'facility_code'})

    if sessions.exists():
        df_sessions = read_frame(sessions.values(
            'facility__object_id', 'start_time', 'end_time', 'session_date', 'enrollment__course__course_category__category_type'
        ))
        utilization, overall_utilization_rate, total_hours_assigned, total_hours_available = calculate_utilization(
            df_sessions, df_facilities, start_date, end_date
        )
    else:
        utilization = df_facilities.copy()
        utilization['hoursAssigned'] = 0
        utilization['hoursAvailable'] = (end_date - start_date).days * 8
        utilization['utilizationRate'] = 0
        overall_utilization_rate = 0
        total_hours_assigned = 0
        total_hours_available = 0

    # FORMAT RESPONSE DATA
    utilization_data = utilization[['facility_code', 'capacity', 'hoursAvailable', 'hoursAssigned', 'utilizationRate', 'branch__branch_name']]
    utilization_data.loc[:, 'classroomName'] = utilization_data.apply(
        lambda row: f"{row['facility_code']} / {row['branch__branch_name']}",
        axis=1
    )
    
    utilization_data = utilization_data.drop(columns=['branch__branch_name'])
    utilization_data = utilization_data.rename(columns={
        'facility_code': 'classroomCode',
        'capacity': 'classroomCapacity'
    }).to_dict(orient='records')

    return {
        "overallUtilizationRate": overall_utilization_rate,
        "totalHoursAssigned": total_hours_assigned,
        "totalHoursAvailable": total_hours_available,
        "classrooms": utilization_data
    }
