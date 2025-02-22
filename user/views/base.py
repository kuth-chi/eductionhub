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
from django.http import response
from django.views.decorators.csrf import csrf_exempt
from user.views.utils import generate_jwt, verify_jwt
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from schools.models.schoolsModel import School, SchoolType


def index(request, type=None):
    
    if type:
        try:
            SCHOOL = School.objects.filter(type__type__iexact = type).distinct()        
        except SchoolType.DoesNotExist:
            SCHOOL = School.objects.none()
    else:
        SCHOOL = School.objects.all()
        
    types = SchoolType.objects.all()
    print(type)
    
    context = {
        "page_title": "Home",
        "header_title": "Home",
        'school_data': SCHOOL, 
        'type_req': type,
        'types': types,
    }

    return render(request, "pages/home.html", context)





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

