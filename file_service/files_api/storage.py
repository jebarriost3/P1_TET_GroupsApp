from pathlib import Path
from uuid import uuid4

from django.conf import settings


def _build_s3_object_url(storage_key: str) -> str:
    if settings.AWS_S3_PUBLIC_BASE_URL:
        return f"{settings.AWS_S3_PUBLIC_BASE_URL.rstrip('/')}/{storage_key}"

    if settings.AWS_S3_BUCKET_NAME and settings.AWS_S3_REGION:
        return (
            f"https://{settings.AWS_S3_BUCKET_NAME}.s3."
            f"{settings.AWS_S3_REGION}.amazonaws.com/{storage_key}"
        )

    raise ValueError("No fue posible construir la URL publica para S3")


def _store_uploaded_file_locally(uploaded_file) -> tuple[str, str]:
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


def _store_uploaded_file_in_s3(uploaded_file) -> tuple[str, str]:
    import boto3

    if not settings.AWS_S3_BUCKET_NAME:
        raise ValueError("AWS_S3_BUCKET_NAME es obligatorio para FILE_STORAGE_BACKEND=s3")

    extension = Path(uploaded_file.name).suffix
    file_name = f"{uuid4().hex}{extension}"
    prefix = settings.AWS_S3_KEY_PREFIX.strip("/")
    storage_key = f"{prefix}/{file_name}" if prefix else file_name

    client = boto3.client(
        "s3",
        region_name=settings.AWS_S3_REGION or None,
        endpoint_url=settings.AWS_S3_ENDPOINT_URL or None,
    )

    extra_args = {}
    content_type = getattr(uploaded_file, "content_type", "") or ""
    if content_type:
        extra_args["ContentType"] = content_type

    client.upload_fileobj(
        uploaded_file.file,
        settings.AWS_S3_BUCKET_NAME,
        storage_key,
        ExtraArgs=extra_args or None,
    )

    return storage_key, _build_s3_object_url(storage_key)


def store_uploaded_file(uploaded_file) -> tuple[str, str]:
    backend = settings.FILE_STORAGE_BACKEND.lower()
    if backend == "s3":
        return _store_uploaded_file_in_s3(uploaded_file)
    return _store_uploaded_file_locally(uploaded_file)
