from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'Admin'

class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'Staff'

class IsAdminOrStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['Admin', 'Staff']

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'Admin':
            return True
        if request.user.role == 'staff' and hasattr(obj, 'branch'):
            return obj.branch == request.user.branch
        return False