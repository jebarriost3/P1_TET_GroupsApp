from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get("username", "").strip()
    password = request.data.get("password", "").strip()
    email = request.data.get("email", "").strip()

    if not username or not password:
        return Response(
            {"detail": "username y password son obligatorios"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {"detail": "Ese username ya existe"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = User.objects.create_user(username=username, password=password, email=email)
    return Response(
        {"id": user.id, "username": user.username, "email": user.email},
        status=status.HTTP_201_CREATED,
    )