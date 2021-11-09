from rest_framework import permissions

from apps.group.models import Group
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


class IsGroupOwnerOrMember(permissions.BasePermission):
    
    def has_object_permission(self, request, view, group):
        """
        Checks if the group is created by current logged in user or he 
        is a member of the group for the retrieve api
        """
        return request.user == group.owner or request.user in group.members.all()
