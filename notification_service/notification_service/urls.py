from django.http import JsonResponse
from django.urls import include, path


urlpatterns = [
    path("health/", lambda request: JsonResponse({"status": "ok", "service": "notification-service"})),
    path("notifications/", include("notifications_api.urls")),
]
