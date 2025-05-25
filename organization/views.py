from django.shortcuts import render
from django.views import View

# Create your views here.
class OrganizationDashboardView(View):
    """ Organization dashboard view """
    template_name = 'organization/dashboard.html'
    
    def get(self, request):
        """ Render organization dashboard """
        template_name = self.template_name
        page_title = "Dashboard"
        
        context = {
            "Title": page_title,
            "Header": page_title
        }
        
        return render(request, template_name, context)