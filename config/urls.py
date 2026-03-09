from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", include("frontend.urls")),

    path("api/health/", lambda request: JsonResponse({"status": "ok"})),
    path("api/auth/", include("accounts.urls")),
    path("api/groups/", include("groups.urls")),
    path("api/chat/", include("chat.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)