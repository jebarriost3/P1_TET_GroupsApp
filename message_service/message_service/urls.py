from django.http import JsonResponse
from django.urls import include, path


urlpatterns = [
    path("health/", lambda request: JsonResponse({"status": "ok", "service": "message-service"})),
    path("", include("message_api.urls")),
]
