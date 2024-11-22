from django.urls import path
from . import views

urlpatterns = [
    # User URLs
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('users/', views.UserList.as_view(), name='user-list'),
    path('users/<str:email>/', views.UserDetail.as_view(), name='user-detail'),
    path('confirm-password/', views.ConfirmPasswordView.as_view(), name='confirm-password'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),

    # Branch URLs
    path('branches/', views.BranchList.as_view(), name='branch-list'),
    path('branches/<str:branch_name>/', views.BranchDetail.as_view(), name='branch-detail'),

    # Course URLs
    path('courses/', views.CourseList.as_view(), name='course-list'),
    path('courses/<str:course_code>/', views.CourseDetail.as_view(), name='course-detail'),

    # Course Category URLs
    path('course-categories/', views.CourseCategoryList.as_view(), name='course-category-list'),
    path('course-categories/<str:category_code>/', views.CourseCategoryDetail.as_view(), name='course-category-detail'),

    # Instructor URLs
    path('instructors/', views.InstructorList.as_view(), name='instructor-list'),
    path('instructors/<str:instructor_code>/', views.InstructorDetail.as_view(), name='instructor-detail'),
    path('create-instructor/', views.CreateInstructor.as_view(), name='create-instructor'),
    path('instructor-sessions/<str:email>', views.InstructorSessions.as_view(), name='instructor-sessions'),
    
    # Vehicle URLs
    path('vehicles/', views.VehicleList.as_view(), name='vehicle-list'),
    path('vehicles/<str:vehicle_code>/', views.VehicleDetail.as_view(), name='vehicle-detail'),

    # Classroom URLs
    path('classrooms/', views.ClassroomList.as_view(), name='classroom-list'),
    path('classrooms/<str:classroom_code>/', views.ClassroomDetail.as_view(), name='classroom-detail'),

    # Facility URLs
    path('facilities/', views.FacilityList.as_view(), name='facility-list'),
    path('facilities/<str:id>/', views.FacilityDetail.as_view(), name='facility-detail'),

    # Student URLs
    path('students/', views.StudentList.as_view(), name='student-list'),
    path('students/<str:student_code>/', views.StudentDetail.as_view(), name='student-detail'),
    path('enroll-student/', views.EnrollStudent.as_view(), name='create-student'),
    path('student-enrollments/<str:identifier>/', views.StudentEnrollments.as_view(), name='student-enrollments'),

    # Enrollment URLs
    path('enrollments/', views.EnrollmentList.as_view(), name='enrollment-list'),
    path('enrollments/<str:enrollment_id>', views.EnrollmentDetail.as_view(), name='enrollment-detail'),

    # Session URLs
    path('sessions/', views.SessionList.as_view(), name='session-list'),
    path('sessions/<str:session_id>/', views.SessionDetail.as_view(), name='session-detail'),
    path('student-sessions/<str:student_code>', views.StudentSessions.as_view(), name='student-sessions'),

    # Analytics
    path('enrollment-trends/', views.EnrollmentTrends.as_view(), name='enrollment-trends'),
    path('resource-stats/', views.ResourceStats.as_view(), name='resource-stats'),
    path('session-trends/', views.SessionTrends.as_view(), name='session-trends'),
    path('classroom-utilization/', views.ClassroomUtilization.as_view(), name='classroom-utilization'),
    path('instructor-utilization/', views.InstructorUtilization.as_view(), name='instructor-utilization'),
    path('vehicle-utilization/', views.VehicleUtilization.as_view(), name='vehicle-utilization'),
    path('schedule-recommendation/', views.ScheduleRecommendation.as_view(), name='schedule-recommendation'),
    path('tdc-schedule-list/', views.TdcScheduleList.as_view(), name='tdc-schedule-list'),
    path('tdc-schedule-match/', views.TdcScheduleMatch.as_view(), name='tdc-schedule-match'),

]