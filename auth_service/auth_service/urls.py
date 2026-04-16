from django.http import JsonResponse
from django.urls import include, path


urlpatterns = [
    path("health/", lambda request: JsonResponse({"status": "ok", "service": "auth-service"})),
    path("auth/", include("auth_api.urls")),
]
