import json
import logging
import time

import pika
from django.conf import settings
from django.core.management.base import BaseCommand

from notifications_api.event_handlers import handle_domain_event


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


class Command(BaseCommand):
    help = "Consume domain events from RabbitMQ and persist notifications"

    def handle(self, *args, **options):
        if not settings.RABBITMQ_ENABLED:
            self.stdout.write(self.style.WARNING("RabbitMQ disabled, notification consumer will not start"))
            return

        while True:
            connection = None
            try:
                connection = pika.BlockingConnection(_build_connection_parameters())
                channel = connection.channel()
                channel.exchange_declare(
                    exchange=settings.RABBITMQ_EXCHANGE,
                    exchange_type="topic",
                    durable=True,
                )
                channel.queue_declare(queue=settings.NOTIFICATION_QUEUE_NAME, durable=True)
                for routing_key in ("group.created", "member.added", "message.created"):
                    channel.queue_bind(
                        exchange=settings.RABBITMQ_EXCHANGE,
                        queue=settings.NOTIFICATION_QUEUE_NAME,
                        routing_key=routing_key,
                    )

                channel.basic_qos(prefetch_count=10)

                def callback(ch, method, properties, body):
                    try:
                        message = json.loads(body.decode("utf-8"))
                        handle_domain_event(message)
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                    except Exception as exc:
                        logger.exception("Failed to process notification event: %s", exc)
                        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

                channel.basic_consume(queue=settings.NOTIFICATION_QUEUE_NAME, on_message_callback=callback)
                self.stdout.write(self.style.SUCCESS("Notification consumer connected to RabbitMQ"))
                channel.start_consuming()
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING("Notification consumer stopped"))
                break
            except Exception as exc:
                logger.warning("Notification consumer connection failed: %s", exc)
                time.sleep(5)
            finally:
                try:
                    if connection and connection.is_open:
                        connection.close()
                except Exception:
                    pass
