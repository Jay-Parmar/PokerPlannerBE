from rest_framework import permissions


class IsGroupOwnerPermission(permissions.BasePermission):
    """
    Permission check for group owner permission
    """
    def has_permission(self, request, view):
        """
        Checks if user is authenticated
        """
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, group):
        """
        Checks if the group is created by current logged in user.
        """
        return request.user == group.owner
