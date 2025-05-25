from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.utils.translation import gettext_lazy as _
# import Internal apps
from administrator.utils import generate_breadcrumbs
from administrator.views import AdminIndexView

# Create your views here.


class AdsDashboardView(View):
    """ Class representing for Ads Manager """
    template_name = "admin-dashboard/ads/index.html"

    def get(self, request):
        """ Display Ads Manager as dashboard """

        template_name = self.template_name
        page_title = _('Ads Manager')
        # Need to set AdminIndexView breadcrumbs as Parent
        parent_breadcrumbs = AdminIndexView.get_breadcrumbs()
        new_breadcrumbs = [{'name': 'Ads Manager', 'url': None}]
        breadcrumbs = generate_breadcrumbs(
            parent_breadcrumbs, *new_breadcrumbs)

        context = {
            "Title": page_title,
            "Header": page_title,
            'breadcrumbs': breadcrumbs,
        }
        return render(request, template_name, context)

    @staticmethod
    def get_breadcrumbs():
        """ Allow other components to use this function"""
        page_title = _('Ads Manager')
        parent_breadcrumbs = AdminIndexView.get_breadcrumbs()
        return generate_breadcrumbs(parent_breadcrumbs, {'name': page_title, 'url': reverse('ads:dashboard')})
