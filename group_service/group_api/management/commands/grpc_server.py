from concurrent import futures

import grpc
from django.conf import settings
from django.core.management.base import BaseCommand

from grpc_contracts import group_service_pb2_grpc
from group_api.grpc_handlers import GroupInternalService


class Command(BaseCommand):
    help = "Run the Group Service internal gRPC server."

    def handle(self, *args, **options):
        address = f"{settings.GROUP_GRPC_HOST}:{settings.GROUP_GRPC_PORT}"
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        group_service_pb2_grpc.add_GroupInternalServiceServicer_to_server(
            GroupInternalService(),
            server,
        )
        server.add_insecure_port(address)
        server.start()

        self.stdout.write(self.style.SUCCESS(f"Group gRPC server listening on {address}"))
        self.stdout.write("Press Ctrl+C to stop.\n")

        try:
            server.wait_for_termination()
        except KeyboardInterrupt:
            self.stdout.write("\nStopping gRPC server...")
            server.stop(grace=2)
