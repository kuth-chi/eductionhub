"""
Base function to handle page
"""
import requests
from django.shortcuts import render

UNSPLASH = requests.get("https://picsum.photos/v2/list?page=2&limit=54", timeout=10).json()

def index(request):
    '''
    Function to render home page
    '''
    template_name = "pages/home.html"
    
    
    image_urls = UNSPLASH    
    context = {
        "page_title": "Home",
        "header_title": "Home",
        'images': image_urls
    }
    return render(request, template_name, context)
