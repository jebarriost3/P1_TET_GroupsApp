from rest_framework import serializers

from .models import Message


class MessageInputSerializer(serializers.Serializer):
    content = serializers.CharField(required=False, allow_blank=True)
    attachment = serializers.FileField(required=False, allow_null=True)


class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source="sender.username", read_only=True)

    class Meta:
        model = Message
        fields = ["id", "group", "sender", "sender_username", "content", "attachment", "created_at"]
        read_only_fields = ["id", "group", "sender", "sender_username", "created_at"]
