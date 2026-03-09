from django.db import models
from django.conf import settings
from groups.models import Group

class Message(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="messages_sent")
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # archivo / imagen
    attachment = models.FileField(upload_to="attachments/", blank=True, null=True)

    def __str__(self):
        return f"[{self.group_id}] {self.sender_id}: {self.content[:30]}"