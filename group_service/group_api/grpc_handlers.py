import grpc

from grpc_contracts import group_service_pb2, group_service_pb2_grpc
from .models import Membership


class GroupInternalService(group_service_pb2_grpc.GroupInternalServiceServicer):
    def CheckMembership(self, request, context):
        membership = (
            Membership.objects.filter(group_id=request.group_id, user_id=request.user_id)
            .only("role")
            .first()
        )

        if not membership:
            return group_service_pb2.CheckMembershipResponse(is_member=False, role="")

        return group_service_pb2.CheckMembershipResponse(
            is_member=True,
            role=membership.role,
        )
