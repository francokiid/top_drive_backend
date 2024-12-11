from datetime import datetime, timedelta
from ....models import Session
from ..utils import get_instructor_utilization


def get_month_range(session_date):
    month_start = session_date.replace(day=1)

    if month_start.month == 12:
        next_month = month_start.replace(year=month_start.year + 1, month=1, day=1)
    else:
        next_month = month_start.replace(month=month_start.month + 1, day=1)
    month_end = next_month - timedelta(days=1)
    
    return month_start, month_end


def get_available_instructors(session_date, start_time, end_time):
    # FORMAT DATE IF STRING
    if isinstance(session_date, str):
        session_date = datetime.strptime(session_date, '%Y-%m-%d')

    # GET BUSY INSTRUCTORS
    busy_instructors = Session.objects.filter(
        session_date=session_date,
        start_time__lt=end_time,
        end_time__gt=start_time,
        status__in=['Completed', 'Scheduled']
    ).exclude(instructor__status='Archived').values_list('instructor__instructor_code', flat=True)

    # GET UTILIZATION DATA FOR THE ENTIRE MONTH
    month_start, month_end = get_month_range(session_date)
    instructor_data = get_instructor_utilization(start_date=month_start, end_date=month_end)

    # FILTER AVAILABLE INSTRUCTORS
    available_instructors = [
        instructor for instructor in instructor_data.get('instructors', [])
        if instructor['instructorCode'] not in busy_instructors
    ]

    return available_instructors


def get_recommended_instructors(category, session_date, start_time, end_time, branch, session_nth, last_session):
    # GET AVAILABLE INSTRUCTORS FOR THE GIVEN DATE AND TIME
    available_instructors = get_available_instructors(session_date, start_time, end_time)

    # SEPARATE INSTRUCTORS BY SENIOR AND REGULAR
    senior_instructors = []
    remaining_instructors = []
    recommended_instructors = []
    
    for instructor in available_instructors:
        instructor_info = {
            'instructorCode': instructor['instructorCode'],
            'instructorName': instructor['instructorName'],
            'branchName': instructor['instructorName'].split(" / ")[-1]
        }
        recommended_instructors.append(instructor_info)
        if "SR" in instructor['instructorName']:
            senior_instructors.append(instructor_info)
        else:
            remaining_instructors.append(instructor_info)

    # PRIORITIZE SENIOR INSTRUCTORS IF FIRST OR LAST SESSION
    if (category == 'PDC') and (session_nth == 1 or session_nth == last_session):
        recommended_instructors = []
        recommended_instructors = senior_instructors + remaining_instructors

    # FILTER INSTRUCTORS FROM SPECIFIED BRANCH
    branch_instructors = [instructor for instructor in recommended_instructors if instructor['branchName'] == branch]
    
    # FALLBACK TO MAIN BRANCH IF NO INSTRUCTORS FOUND FOR SPECIFIED BRANCH
    if not branch_instructors:
        branch_instructors = [instructor for instructor in recommended_instructors if instructor['branchName'] == 'Main']

    # CONSOLIDATE LIST OF INSTRUCTORS, PRIORITIZING THOSE FROM SPECIFIED BRANCH
    other_instructors = [instructor for instructor in recommended_instructors if instructor not in branch_instructors]
    final_instructors = branch_instructors + other_instructors

    return final_instructors