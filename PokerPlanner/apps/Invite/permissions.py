from rest_framework.permissions import BasePermission

from apps.pokerboard.models import Pokerboard


class CustomPermissions(BasePermission):
    """
    Check if requesting user is manager or not
    """
    def has_permission(self, request, view):
        pokerboard_id = request.data['pokerboard']
        pokerboard = Pokerboard.objects.get(id=pokerboard_id)
        return request.user == pokerboard.manager
        