"""
Base function to handle page
"""
from django.http import JsonResponse
import requests
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from user.views.utils import generate_jwt, verify_jwt

UNSPLASH = requests.get("https://picsum.photos/v2/list?page=2&limit=54", timeout=10).json()

import random
import string
import base64
import hashlib


def index(request):
    '''
    Function to render home page
    '''
    code_verifier = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(random.randint(43, 128)))

    code_challenge = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).decode('utf-8').replace('=', '')
    print(code_challenge)
    template_name = "pages/home.html"
    
    
    image_urls = UNSPLASH    
    context = {
        "page_title": "Home",
        "header_title": "Home",
        'images': image_urls
    }
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
