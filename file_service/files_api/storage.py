import os
from pathlib import Path
from uuid import uuid4

from django.conf import settings


def store_uploaded_file(uploaded_file) -> tuple[str, str]:
    storage_root = Path(settings.FILE_STORAGE_ROOT)
    storage_root.mkdir(parents=True, exist_ok=True)

    extension = Path(uploaded_file.name).suffix
    storage_key = f"{uuid4().hex}{extension}"
    destination = storage_root / storage_key

    with destination.open("wb") as output:
        for chunk in uploaded_file.chunks():
            output.write(chunk)

    public_url = f"{settings.FILE_PUBLIC_BASE_URL.rstrip('/')}/media/file_service/{storage_key}"
    return storage_key, public_url
