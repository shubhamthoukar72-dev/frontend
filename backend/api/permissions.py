from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.role == "admin")
        )


class ReadOnlyOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or IsAdminRole().has_permission(request, view)
