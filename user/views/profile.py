""" User app / URLs """
from django.views import View
from django.shortcuts import render
from django.utils.translation import gettext as _

class ProfileView(View):
    def get(self, request):
        template_name = 'profile/index.html'
        page_title = _("Profile")
        context = {
            "Title": page_title,
            "Header": "Profile",
        }
        
        return render(request, template_name, context)