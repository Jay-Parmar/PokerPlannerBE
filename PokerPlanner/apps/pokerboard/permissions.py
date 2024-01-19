from rest_framework.permissions import BasePermission

from apps.pokerboard.models import Pokerboard


class CustomPermissions(BasePermission):

    def has_permission(self, request, view):
        pokerboard_id = view.kwargs['pk']
        pokerboard = Pokerboard.objects.get(id=pokerboard_id)
        if view.action == 'members':
            return request.user == pokerboard.manager
        # only manager can create/delete
        elif view.action == 'invite' and request.method not in ['GET', 'PATCH']:
            return request.user == pokerboard.manager
        return super().has_permission(request, view)
