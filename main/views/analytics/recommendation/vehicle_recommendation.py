from datetime import datetime
from ....models import Session, Facility
from ..utils import get_vehicle_utilization

def get_available_vehicles(session_date, start_time, end_time):
    # GET BUSY VEHICLES FOR THE GIVEN DATE AND TIME
    busy_sessions = Session.objects.filter(
        session_date=session_date,
        start_time__lt=end_time,
        end_time__gt=start_time,
        facility__facility_type='Vehicle'
    ).values_list('facility__object_id', flat=True)

    busy_vehicles = set(busy_sessions)

    if isinstance(session_date, str):
        session_date = datetime.strptime(session_date, '%Y-%m-%d')

    # FETCH VEHICLE UTILIZATION DATA
    vehicle_data = get_vehicle_utilization(end_date=session_date)

    available_vehicles = [
        vehicle for vehicle in vehicle_data.get('vehicles', [])
        if vehicle['vehicleCode'] not in busy_vehicles
    ]

    return available_vehicles


def get_recommended_vehicles(wheel_num, transmission_type, session_date, start_time, end_time, branch):
    WHEEL_NUM_MAP = {
        '2W': '2 Wheels',
        '3W': '3 Wheels',
        '4W': '4 Wheels',
    }

    TRANSMISSION_TYPE_MAP = {
        'MT': 'Manual Transmission',
        'AT': 'Automatic Transmission'
    }

    available_vehicles = get_available_vehicles(session_date, start_time, end_time)

    # FILTER BY WHEEL NUM AND TRANSMISSION TYPE
    filtered_vehicles = [
        vehicle for vehicle in available_vehicles
        if vehicle['wheelNum'] == WHEEL_NUM_MAP.get(wheel_num, '') and 
           vehicle['transmissionType'] == TRANSMISSION_TYPE_MAP.get(transmission_type, '')
    ]

    # FETCH FACILITY DATA
    vehicle_codes = [vehicle['vehicleCode'] for vehicle in filtered_vehicles]
    facilities = Facility.objects.filter(object_id__in=vehicle_codes).values('object_id', 'id')
    facility_map = {facility['object_id']: facility['id'] for facility in facilities}


    # FILTER CLASSROOMS FROM SPECIFIED BRANCH
    branch_vehicles = [
        {
            'vehicleCode': vehicle['vehicleCode'],
            'vehicleName': vehicle['vehicleName'],
            'facilityId': facility_map.get(vehicle['vehicleCode']),
        }
        for vehicle in filtered_vehicles
        if branch in vehicle['vehicleName']
    ]

    # FALLBACK TO MAIN BRANCH IF NO VEHICLES FOUND FOR SPECIFIED BRANCH
    if not branch_vehicles:
        branch_vehicles = [
            {
                'vehicleCode': vehicle['vehicleCode'],
                'vehicleName': vehicle['vehicleName'],
                'facilityId': facility_map.get(vehicle['vehicleCode']),
            }
            for vehicle in filtered_vehicles
            if "Main" in vehicle['vehicleName']
        ]

    # LIST REMAINING VEHICLES FROM OTHER BRANCHES
    other_vehicles = [
        {
            'vehicleCode': vehicle['vehicleCode'],
            'vehicleName': vehicle['vehicleName'],
            'facilityId': facility_map.get(vehicle['vehicleCode']),
        }
        for vehicle in filtered_vehicles
        if vehicle['vehicleCode'] not in [v['vehicleCode'] for v in branch_vehicles]
    ]

    # CONSOLIDATE LIST OF VEHICLES, PRIORITIZING THOSE FROM SPECIFIED BRANCH
    final_vehicles = branch_vehicles + other_vehicles

    return final_vehicles
