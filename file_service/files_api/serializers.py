from rest_framework import serializers

from .models import StoredFile


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class StoredFileSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(source="owner.id", read_only=True)

    class Meta:
        model = StoredFile
        fields = [
            "id",
            "owner_id",
            "storage_key",
            "original_name",
            "content_type",
            "size_bytes",
            "public_url",
            "created_at",
        ]
