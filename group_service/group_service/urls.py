from django.http import JsonResponse
from django.urls import include, path


urlpatterns = [
    path("health/", lambda request: JsonResponse({"status": "ok", "service": "group-service"})),
    path("groups/", include("group_api.urls")),
]
