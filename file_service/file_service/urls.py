from django.http import JsonResponse
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("health/", lambda request: JsonResponse({"status": "ok", "service": "file-service"})),
    path("files/", include("files_api.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
