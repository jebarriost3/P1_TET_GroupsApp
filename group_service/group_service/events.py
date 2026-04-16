import json
import logging
from datetime import datetime, timezone
from uuid import uuid4

import pika
from django.conf import settings


logger = logging.getLogger(__name__)


def _build_connection_parameters() -> pika.ConnectionParameters:
    credentials = pika.PlainCredentials(
        settings.RABBITMQ_USER,
        settings.RABBITMQ_PASSWORD,
    )
    return pika.ConnectionParameters(
        host=settings.RABBITMQ_HOST,
        port=settings.RABBITMQ_PORT,
        virtual_host=settings.RABBITMQ_VHOST,
        credentials=credentials,
        heartbeat=30,
        blocked_connection_timeout=5,
    )


def publish_domain_event(event_type: str, payload: dict) -> bool:
    if not settings.RABBITMQ_ENABLED:
        logger.info("RabbitMQ disabled, skipping event %s", event_type)
        return False

    message = {
        "event_id": str(uuid4()),
        "event_type": event_type,
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
    }

    try:
        connection = pika.BlockingConnection(_build_connection_parameters())
        channel = connection.channel()
        channel.exchange_declare(
            exchange=settings.RABBITMQ_EXCHANGE,
            exchange_type="topic",
            durable=True,
        )
        channel.basic_publish(
            exchange=settings.RABBITMQ_EXCHANGE,
            routing_key=event_type,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=2,
            ),
        )
        connection.close()
        logger.info("Published event %s", event_type)
        return True
    except Exception as exc:
        logger.warning("Failed to publish event %s: %s", event_type, exc)
        return False
