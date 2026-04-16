import json

from django.core.management.base import BaseCommand
from django.conf import settings

from config.events import declare_events_exchange, open_events_connection


class Command(BaseCommand):
    help = "Consume domain events from RabbitMQ and print them to the console."

    def add_arguments(self, parser):
        parser.add_argument(
            "--queue",
            default="groupsapp.dev.events",
            help="Queue name to bind to the configured exchange.",
        )
        parser.add_argument(
            "--binding-key",
            default="#",
            help="Routing key pattern to consume.",
        )

    def handle(self, *args, **options):
        queue_name = options["queue"]
        binding_key = options["binding_key"]

        connection = open_events_connection()
        channel = connection.channel()
        declare_events_exchange(channel)
        channel.queue_declare(queue=queue_name, durable=True)
        channel.queue_bind(
            exchange=settings.RABBITMQ_EXCHANGE,
            queue=queue_name,
            routing_key=binding_key,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Consuming events from queue '{queue_name}' with binding '{binding_key}'"
            )
        )
        self.stdout.write("Press Ctrl+C to stop.\n")

        def callback(ch, method, properties, body):
            try:
                event = json.loads(body.decode("utf-8"))
            except json.JSONDecodeError:
                event = {"raw_body": body.decode("utf-8", errors="replace")}

            self.stdout.write(f"[{method.routing_key}] {json.dumps(event, ensure_ascii=False)}")
            ch.basic_ack(delivery_tag=method.delivery_tag)

        channel.basic_qos(prefetch_count=10)
        channel.basic_consume(queue=queue_name, on_message_callback=callback)

        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            self.stdout.write("\nStopping consumer...")
            channel.stop_consuming()
        finally:
            connection.close()
