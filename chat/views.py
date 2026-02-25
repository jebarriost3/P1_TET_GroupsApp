from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Message
from .serializers import MessageSerializer
from .permissions import IsGroupMember

class GroupMessagesView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsGroupMember]

    def get_queryset(self):
        group_id = self.kwargs["group_id"]
        return Message.objects.filter(group_id=group_id).select_related("sender").order_by("created_at")

    def perform_create(self, serializer):
        group_id = self.kwargs["group_id"]
        serializer.save(group_id=group_id, sender=self.request.user)