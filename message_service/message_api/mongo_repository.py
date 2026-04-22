from datetime import datetime, timezone
from itertools import count

from django.conf import settings
from pymongo import ASCENDING, MongoClient


_client = None
_fallback_id_counter = count(1)


def _get_collection():
    global _client
    if _client is None:
        _client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000)

    database = _client[settings.MONGO_DB_NAME]
    collection = database[settings.MONGO_MESSAGES_COLLECTION]
    collection.create_index([("group_id", ASCENDING), ("created_at", ASCENDING)])
    return collection


def _format_document(document: dict) -> dict:
    return {
        "id": str(document["_id"]),
        "group": document["group_id"],
        "sender": document["sender_id"],
        "sender_username": document.get("sender_username", ""),
        "content": document.get("content", ""),
        "attachment": document.get("attachment"),
        "created_at": document["created_at"].isoformat(),
    }


def list_messages(group_id: int) -> list[dict]:
    collection = _get_collection()
    documents = collection.find({"group_id": int(group_id)}).sort("created_at", ASCENDING)
    return [_format_document(document) for document in documents]


def create_message(group_id: int, sender, content: str, attachment=None) -> dict:
    collection = _get_collection()
    now = datetime.now(timezone.utc)
    document = {
        "group_id": int(group_id),
        "sender_id": int(sender.id),
        "sender_username": sender.username,
        "content": content or "",
        "attachment": attachment,
        "created_at": now,
    }
    result = collection.insert_one(document)
    document["_id"] = result.inserted_id
    return _format_document(document)
