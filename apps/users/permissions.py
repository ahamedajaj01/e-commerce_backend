from rest_framework import permissions

class IsBackofficeStaff(permissions.BasePermission):
    """
    Allows access only to users with a staff role.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_staff or request.user.role is not None)
        )
