import grpc
from django.conf import settings

from grpc_contracts import group_service_pb2, group_service_pb2_grpc
from .models import Membership


def check_group_membership(group_id: int, user_id: int) -> bool:
    address = f"{settings.GROUP_GRPC_HOST}:{settings.GROUP_GRPC_PORT}"

    try:
        with grpc.insecure_channel(address) as channel:
            stub = group_service_pb2_grpc.GroupInternalServiceStub(channel)
            response = stub.CheckMembership(
                group_service_pb2.CheckMembershipRequest(
                    group_id=int(group_id),
                    user_id=int(user_id),
                ),
                timeout=5,
            )
            return response.is_member
    except grpc.RpcError:
        return Membership.objects.filter(
            group_id=int(group_id),
            user_id=int(user_id),
        ).exists()
