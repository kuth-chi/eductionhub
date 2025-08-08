"""
Base function to handle page
"""
from urllib.parse import urlparse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from schools.models.scholarship import Scholarship
from user.views.utils import generate_jwt, verify_jwt
from django.shortcuts import get_object_or_404, render
from schools.models.school import School, SchoolType
from schools.models.scholarship import Scholarship, ScholarshipType
from django.utils.translation import gettext as _

@login_required(login_url="/accounts/login/")
def index(request, type=None):
    if type:
        try:
            SCHOOL = School.objects.filter(type__type__iexact = type).distinct()        
        except SchoolType.DoesNotExist:
            SCHOOL = School.objects.none()
    else:
        SCHOOL = School.objects.all()
        
    types = SchoolType.objects.all()
        
    context = {
        "page_title": "Home",
        "header_title": "Home",
        'school_data': SCHOOL, 
        'type_req': type,
        'types': types,
    }

    return render(request, "pages/home.html", context)

@login_required(login_url="/accounts/login/")
def scholarship(request, type=None):
    
    if type:
        try:
            scholarship_data = Scholarship.objects.filter(type__type__iexact = type).distinct()        
        except SchoolType.DoesNotExist:
            scholarship_data = Scholarship.objects.none()
    else:
        scholarship_data = Scholarship.objects.all()
        
    types = ScholarshipType.objects.all()
        
    context = {
        "page_title": "Home",
        "header_title": "Home",
        'scholarships': scholarship_data, 
        'type_req': type,
        'types': types,
    }

    return render(request, "pages/scholarships.html", context)


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
            import logging
            logger = logging.getLogger(__name__)
            logger.error("Error verifying token", exc_info=True)
            return JsonResponse({'error': 'An error occurred while verifying the token.'}, status=400)
