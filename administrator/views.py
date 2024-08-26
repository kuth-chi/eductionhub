from django.shortcuts import render
from django.views import View
from django.urls import reverse
from django.utils.translation import gettext as _

from .utils import generate_breadcrumbs, get_base_breadcrumbs

# Create your views here.
class AdminIndexView(View):
    """ Admin index view to handle admin dashboard """
    
    def get(self, request):
        """ Admin index view handle admin home page """
        
        template_name = 'admin-dashboard/index.html'
        
        page_title = _('Admin')
        new_crumbs = [{'name': page_title, 'url': None}]

        breadcrumbs = generate_breadcrumbs(get_base_breadcrumbs(), *new_crumbs)
        
        context = {
            "Title": page_title,
            "Header": page_title,
            'breadcrumbs': breadcrumbs,
        }
        return render(request, template_name, context,)
    
    @staticmethod
    def get_breadcrumbs():
        """ Reusable AdminIndexView breadcrumbs """
        page_title = _('Admin')
        return generate_breadcrumbs(get_base_breadcrumbs(), {'name': page_title, 'url': reverse('administrator:dashboard')})