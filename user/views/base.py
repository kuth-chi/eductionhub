"""
Base function to handle page
"""
from django.shortcuts import render


def index(request):
    '''
    Function to render home page
    '''
    template_name = "pages/home.html"
    context = {
        "page_title": "Home",
        "header_title": "Home"
    }
    return render(request, template_name, context)
