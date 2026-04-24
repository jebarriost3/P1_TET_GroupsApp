from django.urls import path

from .views import NotificationDetailView, NotificationListView, mark_notification_as_read


urlpatterns = [
    path("", NotificationListView.as_view(), name="notification-list"),
    path("<int:notification_id>/", NotificationDetailView.as_view(), name="notification-detail"),
    path("<int:notification_id>/read/", mark_notification_as_read, name="notification-read"),
]
