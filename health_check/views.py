import os
import base64
from django.http import JsonResponse
from hashlib import sha256
from django.http import JsonResponse, HttpResponseForbidden


def header_matches_env_var(header_value):
    """
    Returns true if SHA256 of header_value matches WEBSITE_AUTH_ENCRYPTION_KEY.

    :param header_value: Value of the x-ms-auth-internal-token header.
    """
    env_var = os.getenv('WEBSITE_AUTH_ENCRYPTION_KEY')
    if not env_var or not header_value:
        return False

    hash = base64.b64encode(
        sha256(env_var.encode('utf-8')).digest()).decode('utf-8')
    return hash == header_value


def health_check(request):
    auth_header = request.headers.get('x-ms-auth-internal-token')
    if not header_matches_env_var(auth_header):
        return HttpResponseForbidden("Invalid token")

    # Health check logic
    data = {
        "status": "healthy",
        "database": True
    }
    try:
        from django.db import connections
        from django.db.utils import OperationalError
        db_conn = connections['default']
        db_conn.cursor()
    except OperationalError:
        data["database"] = False

    return JsonResponse(data, status=200 if data["database"] else 500)
