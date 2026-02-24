from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Group, Membership


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["id", "name", "created_by", "created_at"]
        read_only_fields = ["id", "created_by", "created_at"]


class AddMemberSerializer(serializers.Serializer):
    username = serializers.CharField()

    def validate_username(self, value):
        if not User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Ese usuario no existe")
        return value