"""
Base function to handle page
"""
from urllib.parse import urlparse
import requests
import random
import string
import base64
import hashlib
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from user.views.utils import generate_jwt, verify_jwt
from django.shortcuts import render
from django.urls import reverse


UNSPLASH = requests.get("https://picsum.photos/v2/list?page=2&limit=54", timeout=10).json()

def index(request):
    '''
    Function to render home page
    '''
    code_verifier = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(random.randint(43, 128)))

    code_challenge = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).decode('utf-8').replace('=', '')
    print(code_challenge)

    # Resolve the URL for 'schools-list' using its namespace and name
    school_url_path = reverse('api:schools-view')
    school_url = request.build_absolute_uri(school_url_path)
    # Use the full URL for the request
    SCHOOL = requests.get(school_url, timeout=10).json()

    image_urls = UNSPLASH    
    context = {
        "page_title": "Home",
        "header_title": "Home",
        'school_data': SCHOOL,  # Include the school data in the context
    }
    
    template_name = "pages/home.html"
    return render(request, template_name, context)




@csrf_exempt
def token_view(request):
    if request.method == 'POST':
        payload = {'user': 'testuser'}
        token = generate_jwt(payload)
        return JsonResponse({'access_token': token})

@csrf_exempt
def verify_token_view(request):
    if request.method == 'POST':
        token = request.POST.get('token')
        try:
            claims = verify_jwt(token)
            return JsonResponse({'claims': claims})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

