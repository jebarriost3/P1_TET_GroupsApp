from rest_framework import serializers

from .models import Message


class MessageInputSerializer(serializers.Serializer):
    content = serializers.CharField(required=False, allow_blank=True)
    attachment_id = serializers.IntegerField(required=False, allow_null=True, min_value=1)


class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source="sender.username", read_only=True)
    attachment = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ["id", "group", "sender", "sender_username", "content", "attachment", "created_at"]
        read_only_fields = ["id", "group", "sender", "sender_username", "created_at"]

    def get_attachment(self, obj):
        attachments = self.context.get("attachments", {})
        return attachments.get(obj.pk)
