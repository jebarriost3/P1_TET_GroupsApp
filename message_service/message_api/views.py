from django.conf import settings
from django.db import transaction
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from message_service.events import publish_domain_event
from .models import Message
from .mongo_repository import create_message, list_messages
from .permissions import IsGroupMember
from .serializers import MessageInputSerializer, MessageSerializer


class PostgresGroupMessagesView(generics.ListCreateAPIView):
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


class MongoGroupMessagesView(APIView):
    permission_classes = [IsAuthenticated, IsGroupMember]

    def get(self, request, group_id: int):
        return Response(list_messages(group_id))

    def post(self, request, group_id: int):
        serializer = MessageInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        message = create_message(
            group_id=group_id,
            sender=request.user,
            content=serializer.validated_data.get("content", ""),
            attachment=None,
        )

        publish_domain_event(
            "message.created",
            {
                "message_id": message["id"],
                "group_id": message["group"],
                "sender_id": message["sender"],
                "content": message["content"],
                "has_attachment": bool(message["attachment"]),
                "created_at": message["created_at"],
            },
        )

        return Response(message, status=status.HTTP_201_CREATED)


GroupMessagesView = (
    MongoGroupMessagesView
    if settings.MESSAGE_STORAGE == "mongo"
    else PostgresGroupMessagesView
)
