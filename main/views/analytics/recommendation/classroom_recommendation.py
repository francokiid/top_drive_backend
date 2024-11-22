from datetime import datetime
from ....models import Session, Facility
from ..utils import get_classroom_utilization


def get_available_classrooms(session_date, start_time, end_time):
    # GET BUSY CLASSROOMS FOR THE GIVEN DATE AND TIME
    busy_sessions = Session.objects.filter(
        session_date=session_date,
        start_time__lt=end_time,
        end_time__gt=start_time,
        facility__facility_type='Classroom'
    ).values_list('facility__object_id', flat=True)

    busy_classrooms = set(busy_sessions)

    if isinstance(session_date, str):
        session_date = datetime.strptime(session_date, '%Y-%m-%d')

    # FETCH CLASSROOM UTILIZATION DATA
    classroom_data = get_classroom_utilization(end_date=session_date)

    available_classrooms = [
        classroom for classroom in classroom_data.get('classrooms', [])
        if classroom['classroomCode'] not in busy_classrooms
    ]

    return available_classrooms


def get_recommended_classrooms(wheel_num, transmission_type, session_date, start_time, end_time, branch):
    available_classrooms = get_available_classrooms(session_date, start_time, end_time)

    # FILTER CLASSROOMS
    filtered_classrooms = [
        classroom for classroom in available_classrooms
    ]
    
    # FETCH FACILITY DATA
    classroom_codes = [classroom['classroomCode'] for classroom in filtered_classrooms]
    facilities = Facility.objects.filter(object_id__in=classroom_codes).values('object_id', 'id')
    facility_map = {facility['object_id']: facility['id'] for facility in facilities}

    # FILTER CLASSROOMS FROM SPECIFIED BRANCH
    branch_classrooms = [
        {
            'classroomCode': classroom['classroomCode'],
            'classroomName': classroom['classroomName'],
            'facilityId': facility_map.get(classroom['classroomCode']),
        }
        for classroom in filtered_classrooms
        if branch in classroom['classroomName']
    ]

    # FALLBACK TO MAIN BRANCH IF NO CLASSROOMS FOUND FOR SPECIFIED BRANCH
    if not branch_classrooms:
        branch_classrooms = [
            {
                'classroomCode': classroom['classroomCode'],
                'classroomName': classroom['classroomName'],
                'facilityId': facility_map.get(classroom['classroomCode']),
            }
            for classroom in filtered_classrooms
            if "Main" in classroom['classroomName']
        ]

    # LIST REMAINING CLASSROOMS FROM OTHER BRANCHES
    other_classrooms = [
        {
            'classroomCode': classroom['classroomCode'],
            'classroomName': classroom['classroomName'],
            'facilityId': facility_map.get(classroom['classroomCode']),
        }
        for classroom in filtered_classrooms
        if classroom['classroomCode'] not in [c['classroomCode'] for c in branch_classrooms]
    ]

    # CONSOLIDATE LIST OF CLASSROOMS, PRIORITIZING THOSE FROM SPECIFIED BRANCH
    final_classrooms = branch_classrooms + other_classrooms

    return final_classrooms
