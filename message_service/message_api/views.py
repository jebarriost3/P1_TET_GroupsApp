from django.db import transaction
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from message_service.events import publish_domain_event
from .models import Message
from .permissions import IsGroupMember
from .serializers import MessageSerializer


class GroupMessagesView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsGroupMember]

    def get_queryset(self):
        group_id = self.kwargs["group_id"]
        return Message.objects.filter(group_id=group_id).select_related("sender").order_by("created_at")

    def perform_create(self, serializer):
        group_id = self.kwargs["group_id"]
        message = serializer.save(group_id=group_id, sender=self.request.user)

        transaction.on_commit(
            lambda: publish_domain_event(
                "message.created",
                {
                    "message_id": message.id,
                    "group_id": message.group_id,
                    "sender_id": self.request.user.id,
                    "content": message.content,
                    "has_attachment": bool(message.attachment),
                    "created_at": message.created_at.isoformat(),
                },
            )
        )
