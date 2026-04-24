import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt


HOP_BY_HOP_HEADERS = {
    "host",
    "content-length",
    "connection",
    "accept-encoding",
}


def _build_target_url(base_url: str, path: str, query_params) -> str:
    clean_base = base_url.rstrip("/")
    clean_path = path.lstrip("/")
    url = f"{clean_base}/{clean_path}" if clean_path else clean_base

    if query_params:
        query_string = urlencode(list(query_params.lists()), doseq=True)
        if query_string:
            url = f"{url}?{query_string}"

    return url


def _proxy_request(request, base_url: str, path: str) -> HttpResponse:
    target_url = _build_target_url(base_url, path, request.GET)
    body = request.body if request.method not in {"GET", "HEAD"} else None

    proxied_headers = {
        key: value
        for key, value in request.headers.items()
        if key.lower() not in HOP_BY_HOP_HEADERS
    }

    upstream_request = Request(
        url=target_url,
        data=body,
        headers=proxied_headers,
        method=request.method,
    )

    try:
        with urlopen(upstream_request, timeout=15) as upstream_response:
            response_body = upstream_response.read()
            content_type = upstream_response.headers.get("Content-Type", "application/json")
            response = HttpResponse(
                response_body,
                status=upstream_response.status,
                content_type=content_type,
            )
            return response
    except HTTPError as exc:
        response_body = exc.read()
        content_type = exc.headers.get("Content-Type", "application/json")
        return HttpResponse(response_body, status=exc.code, content_type=content_type)
    except URLError as exc:
        return JsonResponse(
            {
                "detail": "No fue posible conectar con el servicio de destino",
                "service_url": base_url,
                "reason": str(exc.reason),
            },
            status=502,
        )
    except Exception as exc:
        return JsonResponse(
            {
                "detail": "Error inesperado en el API Gateway",
                "error": str(exc),
            },
            status=502,
        )


@csrf_exempt
def proxy_to_auth(request, path: str = ""):
    target_path = f"auth/{path}" if path else "auth/"
    return _proxy_request(request, settings.AUTH_SERVICE_URL, target_path)


@csrf_exempt
def proxy_to_groups(request, path: str = ""):
    target_path = f"groups/{path}" if path else "groups/"
    return _proxy_request(request, settings.GROUP_SERVICE_URL, target_path)


@csrf_exempt
def proxy_to_messages(request, path: str = ""):
    return _proxy_request(request, settings.MESSAGE_SERVICE_URL, path)


@csrf_exempt
def proxy_to_files(request, path: str = ""):
    target_path = f"files/{path}" if path else "files/"
    return _proxy_request(request, settings.FILE_SERVICE_URL, target_path)


@csrf_exempt
def proxy_to_notifications(request, path: str = ""):
    target_path = f"notifications/{path}" if path else "notifications/"
    return _proxy_request(request, settings.NOTIFICATION_SERVICE_URL, target_path)
