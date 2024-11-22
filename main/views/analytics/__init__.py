from .recommendation.schedule_recommendation import ScheduleRecommendation
from .recommendation.tdc_schedule_list import TdcScheduleList
from .recommendation.tdc_match import TdcScheduleMatch
from .recommendation.instructor_recommendation import get_available_instructors, get_recommended_instructors
from .recommendation.vehicle_recommendation import get_recommended_vehicles
from .reports.classroom import ClassroomUtilization
from .reports.instructor import InstructorUtilization
from .reports.vehicle import VehicleUtilization
from .stats.enrollment import EnrollmentTrends
from .stats.resource import ResourceStats
from .stats.session import SessionTrends