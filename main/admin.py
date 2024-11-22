from django.contrib import admin
from .models import Branch, CourseCategory, Course, Instructor, Vehicle, Student, Enrollment, Session

admin.site.register(Branch)
admin.site.register(CourseCategory)
admin.site.register(Course)
admin.site.register(Instructor)
admin.site.register(Vehicle)
admin.site.register(Student)
admin.site.register(Enrollment)
admin.site.register(Session)