from django.shortcuts import render
from django.utils.translation import gettext as _


# Create your views here.
def about_us(request):
    template_name='pages/about.html'
    
    page_title = _('About Us')

    context = {
        "page_title": page_title,
    }

    return render(request, template_name, context)

def our_privacy(request):
    template_name = 'pages/privacy.html'

    page_title = _('Privacy Policy')

    context = {
        "page_title": page_title
    }
    return render(request, template_name, context)

def terms_conditions(request):
    template_name = 'pages/terms-conditions.html'

    page_title = _('Terms And Conditions')

    context = {
        "page_title": page_title
    }
    return render(request, template_name, context)