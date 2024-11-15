from typing import Any
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView

from schools.models.schoolsModel import School


class IndexView(TemplateView):
    """School index page handler"""
    template_name = 'schools/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "title": "School Index",
            "active": True,
        })
        return context


class SchoolDetailView(DetailView):
    '''
        Handle school information details
    '''
    template = 'schools/details.html'
    model = School

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context = {
            "title": "School Detail",
            "active": True,
        }
        return context
