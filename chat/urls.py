from django.urls import path
from .views import GroupMessagesView

urlpatterns = [
    path("groups/<int:group_id>/messages/", GroupMessagesView.as_view(), name="group-messages"),
]