# chat/permissions.py
from rest_framework.permissions import BasePermission
from groups.models import Membership
class IsGroupMember(BasePermission):
    def has_permission(self, request, view):
        group_id = view.kwargs.get("group_id")

        if not request.user or not request.user.is_authenticated:
            return False

        if not group_id:
            return False

        return Membership.objects.filter(group_id=group_id, user=request.user).exists()