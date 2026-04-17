from django.conf import settings
from django.db import models


class Group(models.Model):
    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="message_service_created_groups",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "groups_group"
        managed = False


class Membership(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="message_service_memberships",
    )
    role = models.CharField(max_length=10)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "groups_membership"
        managed = False


class Message(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="messages_sent",
    )
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    attachment = models.FileField(upload_to="attachments/", blank=True, null=True)

    class Meta:
        db_table = "chat_message"

    def __str__(self):
        return f"[{self.group_id}] {self.sender_id}: {self.content[:30]}"
