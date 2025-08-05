# views.py
from django.conf import settings
from django.views.decorators.http import require_GET
from django.http import JsonResponse
import requests
from django.core.cache import cache

@require_GET
def client_ip_info(request):
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
    if not ip:
        return JsonResponse({'ip': None}, status=400)

    cached = cache.get(f'ipinfo:{ip}')
    if cached:
        return JsonResponse(cached)

    token = settings.IPINFO_TOKEN  # keep in your env
    res = requests.get(f'https://ipinfo.io/{ip}/json?token={token}')
    if res.status_code != 200:
        return JsonResponse({'ip': ip})

    data = res.json()
    cache.set(f'ipinfo:{ip}', data, timeout=60 * 60 * 6)  # Cache 6 hours
    return JsonResponse(data)
