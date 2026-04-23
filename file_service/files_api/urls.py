from django.urls import path

from .views import StoredFileDetailView, upload_file


urlpatterns = [
    path("upload/", upload_file, name="file-upload"),
    path("<int:file_id>/", StoredFileDetailView.as_view(), name="file-detail"),
]
