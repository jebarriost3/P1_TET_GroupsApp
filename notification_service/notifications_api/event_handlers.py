import logging
from typing import Iterable

from django.contrib.auth.models import User
from django.db import connection

from .models import Notification


logger = logging.getLogger(__name__)


def _fetch_group_name(group_id: int) -> str:
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT name FROM groups_group WHERE id = %s",
            [group_id],
        )
        row = cursor.fetchone()
    return row[0] if row else f"Grupo {group_id}"


def _fetch_group_member_ids(group_id: int, exclude_user_id: int | None = None) -> list[int]:
    sql = "SELECT user_id FROM groups_membership WHERE group_id = %s"
    params: list[int] = [group_id]
    if exclude_user_id is not None:
        sql += " AND user_id <> %s"
        params.append(exclude_user_id)

    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        rows = cursor.fetchall()

    return [row[0] for row in rows]


def _fetch_username(user_id: int) -> str:
    return User.objects.filter(id=user_id).values_list("username", flat=True).first() or f"user-{user_id}"


def _build_notification_rows(event_id: str, event_type: str, payload: dict) -> Iterable[Notification]:
    if event_type == "group.created":
        recipient_id = payload.get("created_by")
        if not recipient_id:
            return []
        group_name = payload.get("name") or _fetch_group_name(payload["group_id"])
        return [
            Notification(
                recipient_id=recipient_id,
                event_id=event_id,
                event_type=event_type,
                title="Grupo creado",
                body=f"Se creo el grupo {group_name}.",
                metadata=payload,
            )
        ]

    if event_type == "member.added":
        recipient_id = payload.get("added_user_id")
        if not recipient_id:
            return []
        group_name = payload.get("group_name") or _fetch_group_name(payload["group_id"])
        added_by_id = payload.get("added_by_id")
        added_by_username = payload.get("added_by_username") or (
            _fetch_username(added_by_id) if added_by_id else "Un administrador"
        )
        return [
            Notification(
                recipient_id=recipient_id,
                event_id=event_id,
                event_type=event_type,
                title="Te agregaron a un grupo",
                body=f"{added_by_username} te agrego al grupo {group_name}.",
                metadata=payload,
            )
        ]

    if event_type == "message.created":
        group_id = payload.get("group_id")
        sender_id = payload.get("sender_id")
        if not group_id or not sender_id:
            return []
        recipient_ids = _fetch_group_member_ids(group_id, exclude_user_id=sender_id)
        if not recipient_ids:
            return []
        sender_username = payload.get("sender_username") or _fetch_username(sender_id)
        group_name = payload.get("group_name") or _fetch_group_name(group_id)
        content_preview = (payload.get("content") or "").strip()
        if content_preview:
            content_preview = content_preview[:80]
        else:
            content_preview = "Envio un adjunto."
        return [
            Notification(
                recipient_id=recipient_id,
                event_id=event_id,
                event_type=event_type,
                title=f"Nuevo mensaje en {group_name}",
                body=f"{sender_username}: {content_preview}",
                metadata=payload,
            )
            for recipient_id in recipient_ids
        ]

    return []


def handle_domain_event(message: dict) -> int:
    event_id = message.get("event_id")
    event_type = message.get("event_type")
    payload = message.get("payload") or {}

    if not event_id or not event_type:
        logger.warning("Skipping malformed event: %s", message)
        return 0

    notifications = list(_build_notification_rows(event_id, event_type, payload))
    if not notifications:
        logger.info("No notifications generated for event %s", event_type)
        return 0

    created = Notification.objects.bulk_create(notifications, ignore_conflicts=True)
    logger.info("Stored %s notifications for event %s", len(created), event_type)
    return len(created)
