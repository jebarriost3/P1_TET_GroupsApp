from django.conf import settings
from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from message_service.events import publish_domain_event
from .models import Message
from .file_client import FileServiceError, extract_authorization_header, fetch_file_metadata
from .mongo_repository import create_message, list_messages
from .permissions import IsGroupMember
from .serializers import MessageInputSerializer, MessageSerializer


def _build_attachment_map(raw_messages, authorization_header: str) -> dict:
    attachment_map = {}
    for raw_message in raw_messages:
        attachment_ref = None
        if isinstance(raw_message, Message):
            attachment_ref = getattr(raw_message.attachment, "name", "") or ""
            key = raw_message.pk
        else:
            attachment_ref = raw_message.get("attachment_id")
            key = raw_message["id"]

        if not attachment_ref:
            attachment_map[key] = None
            continue

        try:
            attachment_id = int(attachment_ref)
        except (TypeError, ValueError):
            attachment_map[key] = {"legacy_reference": attachment_ref}
            continue

        attachment_map[key] = fetch_file_metadata(attachment_id, authorization_header)

    return attachment_map


class PostgresGroupMessagesView(APIView):
    permission_classes = [IsAuthenticated, IsGroupMember]

    def _get_queryset(self):
        group_id = self.kwargs["group_id"]
        return Message.objects.filter(group_id=group_id).select_related("sender").order_by("created_at")

    def get(self, request, group_id: int):
        messages = list(self._get_queryset())
        attachment_map = _build_attachment_map(messages, extract_authorization_header(request))
        serializer = MessageSerializer(
            messages,
            many=True,
            context={"attachments": attachment_map},
        )
        return Response(serializer.data)

    def post(self, request, group_id: int):
        serializer = MessageInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        attachment_id = serializer.validated_data.get("attachment_id")
        attachment_reference = None
        attachment_metadata = None
        authorization_header = extract_authorization_header(request)
        if attachment_id:
            try:
                attachment_metadata = fetch_file_metadata(attachment_id, authorization_header)
            except FileServiceError as exc:
                raise ValidationError({"attachment_id": str(exc)}) from exc
            attachment_reference = str(attachment_id)

        message = Message.objects.create(
            group_id=group_id,
            sender=request.user,
            content=serializer.validated_data.get("content", ""),
            attachment=attachment_reference,
        )

        transaction.on_commit(
            lambda: publish_domain_event(
                "message.created",
                {
                    "message_id": message.id,
                    "group_id": message.group_id,
                    "sender_id": self.request.user.id,
                    "content": message.content,
                    "has_attachment": bool(attachment_reference),
                    "created_at": message.created_at.isoformat(),
                },
            )
        )

        response_serializer = MessageSerializer(
            message,
            context={"attachments": {message.pk: attachment_metadata}},
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class MongoGroupMessagesView(APIView):
    permission_classes = [IsAuthenticated, IsGroupMember]

    def get(self, request, group_id: int):
        messages = list_messages(group_id)
        attachment_map = _build_attachment_map(messages, extract_authorization_header(request))

        for message in messages:
            message["attachment"] = attachment_map.get(message["id"])
            message.pop("attachment_id", None)

        return Response(messages)

    def post(self, request, group_id: int):
        serializer = MessageInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        attachment_id = serializer.validated_data.get("attachment_id")
        attachment_metadata = None
        if attachment_id:
            try:
                attachment_metadata = fetch_file_metadata(
                    attachment_id,
                    extract_authorization_header(request),
                )
            except FileServiceError as exc:
                raise ValidationError({"attachment_id": str(exc)}) from exc

        message = create_message(
            group_id=group_id,
            sender=request.user,
            content=serializer.validated_data.get("content", ""),
            attachment_id=attachment_id,
        )
        message["attachment"] = attachment_metadata

        publish_domain_event(
            "message.created",
            {
                "message_id": message["id"],
                "group_id": message["group"],
                "sender_id": message["sender"],
                "content": message["content"],
                "has_attachment": bool(attachment_id),
                "created_at": message["created_at"],
            },
        )

        return Response(message, status=status.HTTP_201_CREATED)


GroupMessagesView = (
    MongoGroupMessagesView
    if settings.MESSAGE_PERSISTENCE_BACKEND == "mongo"
    else PostgresGroupMessagesView
)
