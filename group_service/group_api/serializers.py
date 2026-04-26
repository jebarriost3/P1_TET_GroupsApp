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


class MembershipSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    is_online = serializers.SerializerMethodField()

    class Meta:
        model = Membership
        fields = ["id", "username", "role", "joined_at", "is_online"]

    def get_is_online(self, obj):
        online_user_ids = self.context.get("online_user_ids", set())
        return obj.user_id in online_user_ids
