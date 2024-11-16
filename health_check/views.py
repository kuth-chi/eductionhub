from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.


def health_check(request):
    ''' This is a helper function to check the health of applications '''
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