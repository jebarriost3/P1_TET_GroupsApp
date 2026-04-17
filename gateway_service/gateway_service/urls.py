from django.http import JsonResponse
from django.urls import include, path, re_path

from gateway_api.views import proxy_to_auth, proxy_to_groups, proxy_to_messages


urlpatterns = [
    path("", include("gateway_api.frontend_urls")),
    path("health/", lambda request: JsonResponse({"status": "ok", "service": "gateway-service"})),
    path("api/health/", lambda request: JsonResponse({"status": "ok", "service": "gateway-service"})),
    re_path(r"^api/auth/(?P<path>.*)$", proxy_to_auth),
    re_path(r"^api/groups/(?P<path>.*)$", proxy_to_groups),
    re_path(r"^api/chat/(?P<path>.*)$", proxy_to_messages),
]
