# Add this to api/views.py or create a new debug view
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


@csrf_exempt
@require_http_methods(["GET"])
def debug_cookies_backend(request):
    """Debug endpoint to see what cookies Django receives"""

    cookies_received = dict(request.COOKIES)
    headers_received = dict(request.META)

    # Filter headers to show relevant ones
    relevant_headers = {k: v for k, v in headers_received.items()
                        if k.startswith('HTTP_') or k in ['CONTENT_TYPE', 'REQUEST_METHOD']}

    debug_info = {
        'timestamp': str(request.META.get('REQUEST_TIME', 'unknown')),
        'method': request.method,
        'path': request.path,
        'cookies_received': cookies_received,
        'has_access_token': 'access_token' in cookies_received,
        'has_refresh_token': 'refresh_token' in cookies_received,
        'has_csrftoken': 'csrftoken' in cookies_received,
        'auth_header': request.META.get('HTTP_AUTHORIZATION', 'Not present'),
        'origin': request.META.get('HTTP_ORIGIN', 'Not present'),
        'user_agent': request.META.get('HTTP_USER_AGENT', 'Not present'),
        'host': request.META.get('HTTP_HOST', 'Not present'),
        'relevant_headers': relevant_headers,
    }

    return JsonResponse(debug_info)
