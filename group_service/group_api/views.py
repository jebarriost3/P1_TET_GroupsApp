from datetime import timedelta

from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from group_service.events import publish_domain_event
from .models import Group, Membership
from .serializers import AddMemberSerializer, GroupSerializer, MembershipSerializer


ONLINE_WINDOW_SECONDS = 45
_presence_by_user_id = {}


def _touch_presence(user_id: int) -> None:
    _presence_by_user_id[int(user_id)] = timezone.now()


def _online_user_ids(user_ids) -> set[int]:
    now = timezone.now()
    return {
        int(user_id)
        for user_id in user_ids
        if (now - _presence_by_user_id.get(int(user_id), now - timedelta(days=1))).total_seconds()
        <= ONLINE_WINDOW_SECONDS
    }


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def groups_list_create(request):
    _touch_presence(request.user.id)

    if request.method == "GET":
        groups = Group.objects.filter(memberships__user=request.user).distinct()
        return Response(GroupSerializer(groups, many=True).data)

    serializer = GroupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    group = Group.objects.create(
        name=serializer.validated_data["name"],
        created_by=request.user,
    )
    Membership.objects.create(group=group, user=request.user, role="admin")

    transaction.on_commit(
        lambda: publish_domain_event(
            "group.created",
            {
                "group_id": group.id,
                "name": group.name,
                "created_by": request.user.id,
            },
        )
    )

    return Response(GroupSerializer(group).data, status=status.HTTP_201_CREATED)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def group_members(request, group_id: int):
    _touch_presence(request.user.id)

    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return Response({"detail": "Grupo no existe"}, status=status.HTTP_404_NOT_FOUND)

    is_member = Membership.objects.filter(group=group, user=request.user).exists()
    if not is_member:
        return Response({"detail": "No perteneces a este grupo"}, status=status.HTTP_403_FORBIDDEN)

    if request.method == "GET":
        memberships = (
            Membership.objects.filter(group=group)
            .select_related("user")
            .order_by("role", "user__username")
        )
        member_user_ids = [membership.user_id for membership in memberships]
        serializer = MembershipSerializer(
            memberships,
            many=True,
            context={"online_user_ids": _online_user_ids(member_user_ids)},
        )
        return Response(serializer.data)

    is_admin = Membership.objects.filter(group=group, user=request.user, role="admin").exists()
    if not is_admin:
        return Response({"detail": "Solo admin puede agregar miembros"}, status=status.HTTP_403_FORBIDDEN)

    serializer = AddMemberSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user_to_add = User.objects.get(username=serializer.validated_data["username"])
    membership, created = Membership.objects.get_or_create(
        group=group,
        user=user_to_add,
        defaults={"role": "member"},
    )

    if created:
        transaction.on_commit(
            lambda: publish_domain_event(
                "member.added",
                {
                    "group_id": group.id,
                    "group_name": group.name,
                    "added_user_id": user_to_add.id,
                    "added_username": user_to_add.username,
                    "added_by_id": request.user.id,
                    "added_by_username": request.user.username,
                    "role": membership.role,
                },
            )
        )
        detail = f"Usuario {user_to_add.username} agregado al grupo"
    else:
        detail = f"Usuario {user_to_add.username} ya pertenece al grupo"

    return Response({"detail": detail}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mark_presence(request):
    _touch_presence(request.user.id)
    return Response({"status": "online", "online_window_seconds": ONLINE_WINDOW_SECONDS})
