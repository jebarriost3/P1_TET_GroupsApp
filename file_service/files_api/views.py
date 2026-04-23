from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import StoredFile
from .serializers import FileUploadSerializer, StoredFileSerializer
from .storage import store_uploaded_file


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def upload_file(request):
    serializer = FileUploadSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    uploaded_file = serializer.validated_data["file"]
    storage_key, public_url = store_uploaded_file(uploaded_file)

    stored_file = StoredFile.objects.create(
        owner=request.user,
        storage_key=storage_key,
        original_name=uploaded_file.name,
        content_type=getattr(uploaded_file, "content_type", "") or "",
        size_bytes=uploaded_file.size,
        public_url=public_url,
    )

    return Response(StoredFileSerializer(stored_file).data, status=status.HTTP_201_CREATED)


class StoredFileDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StoredFileSerializer
    queryset = StoredFile.objects.all()
    lookup_url_kwarg = "file_id"
