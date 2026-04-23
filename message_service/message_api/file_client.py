import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings


class FileServiceError(Exception):
    pass


def extract_authorization_header(request) -> str:
    return request.headers.get("Authorization", "")


def fetch_file_metadata(file_id: int, authorization_header: str = "") -> dict:
    target_url = f"{settings.FILE_SERVICE_URL.rstrip('/')}/files/{int(file_id)}/"
    headers = {}
    if authorization_header:
        headers["Authorization"] = authorization_header

    upstream_request = Request(url=target_url, headers=headers, method="GET")

    try:
        with urlopen(upstream_request, timeout=10) as upstream_response:
            return json.loads(upstream_response.read().decode("utf-8"))
    except HTTPError as exc:
        if exc.code == 404:
            raise FileServiceError("Archivo no encontrado") from exc
        if exc.code == 401:
            raise FileServiceError("No fue posible autenticar contra el servicio de archivos") from exc
        if exc.code == 403:
            raise FileServiceError("No tienes permisos sobre el archivo solicitado") from exc
        raise FileServiceError("Error al consultar el servicio de archivos") from exc
    except (URLError, TimeoutError) as exc:
        raise FileServiceError("No fue posible conectar con el servicio de archivos") from exc
