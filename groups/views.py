from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Group, Membership
from .serializers import GroupSerializer, AddMemberSerializer


@api_view(["GET", "POST"])
def groups_list_create(request):
    if request.method == "GET":
        # Mis grupos (donde soy miembro)
        groups = Group.objects.filter(memberships__user=request.user).distinct()
        return Response(GroupSerializer(groups, many=True).data)

    # POST: crear grupo y crear membership admin
    serializer = GroupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    group = Group.objects.create(
        name=serializer.validated_data["name"],
        created_by=request.user,
    )
    Membership.objects.create(group=group, user=request.user, role="admin")
    return Response(GroupSerializer(group).data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def add_member(request, group_id: int):
    # Solo admin puede agregar
    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return Response({"detail": "Grupo no existe"}, status=status.HTTP_404_NOT_FOUND)

    is_admin = Membership.objects.filter(group=group, user=request.user, role="admin").exists()
    if not is_admin:
        return Response({"detail": "Solo admin puede agregar miembros"}, status=status.HTTP_403_FORBIDDEN)

    serializer = AddMemberSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user_to_add = User.objects.get(username=serializer.validated_data["username"])
    Membership.objects.get_or_create(group=group, user=user_to_add, defaults={"role": "member"})
    return Response({"detail": f"Usuario {user_to_add.username} agregado al grupo"}, status=status.HTTP_200_OK)