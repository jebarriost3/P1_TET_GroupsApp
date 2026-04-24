from django.conf import settings
from django.http import JsonResponse
from django.urls import include, path, re_path
from django.views.static import serve

from gateway_api.views import (
    proxy_to_auth,
    proxy_to_files,
    proxy_to_groups,
    proxy_to_messages,
    proxy_to_notifications,
)


urlpatterns = [
    path("", include("gateway_api.frontend_urls")),
    path("health/", lambda request: JsonResponse({"status": "ok", "service": "gateway-service"})),
    path("api/health/", lambda request: JsonResponse({"status": "ok", "service": "gateway-service"})),
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
    re_path(r"^api/auth/(?P<path>.*)$", proxy_to_auth),
    re_path(r"^api/groups/(?P<path>.*)$", proxy_to_groups),
    re_path(r"^api/chat/(?P<path>.*)$", proxy_to_messages),
    re_path(r"^api/files/(?P<path>.*)$", proxy_to_files),
    re_path(r"^api/notifications/(?P<path>.*)$", proxy_to_notifications),
]
