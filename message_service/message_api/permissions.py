from rest_framework.permissions import BasePermission

from .group_client import check_group_membership


class IsGroupMember(BasePermission):
    def has_permission(self, request, view):
        group_id = view.kwargs.get("group_id")

        if not request.user or not request.user.is_authenticated:
            return False

        if not group_id:
            return False

        return check_group_membership(group_id=group_id, user_id=request.user.id)
