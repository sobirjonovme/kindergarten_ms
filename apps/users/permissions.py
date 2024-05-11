from rest_framework.permissions import BasePermission

from apps.users.choices import UserTypes


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user.is_authenticated and user.type == UserTypes.ADMIN)
