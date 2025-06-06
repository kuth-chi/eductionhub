import uuid
import logging
from django.db.models import Q
from typing import Any
from django import forms
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

from schools.models.OnlineProfile import PlatformProfile
from schools.models.schoolsModel import School, SchoolType

logger = logging.getLogger(__name__)

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


class SchoolCreateView(LoginRequiredMixin, CreateView):
    ''' This is extended CreateView class to generate dynamic forms for School models '''
    model = School
    template_name = "schools/create.html"
    success_url = reverse_lazy("schools:index")
    fields = ("name", "logo", "local_name", "short_name", "description",
              "established", "type", "founder", "president", "endowment", "location")

    login_url = reverse_lazy('profiles:login')  
    redirect_field_name = 'next'  

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if 'type' in form.fields:
            form.fields['type'].queryset = SchoolType.objects.all()
            form.fields['type'].required = False
            form.fields['type'].widget = forms.SelectMultiple(attrs={
                "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
            })
        else:
            print("❌ Type field is missing in form!")

        return form



    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "School Creation Form"
        ctx["active_class"] = "active"
        ctx["page_name"] = "create"
        ctx["uuid"] = str(uuid.uuid4())
        return ctx

    def form_valid(self, form):
        form.cleaned_data['type'] = form.cleaned_data.get('type') or []
        if not form.instance.uuid:
            form.instance.uuid = uuid.uuid4()
        form.instance.logo = self.request.FILES.get('logo')

        messages.success(self.request, "School has been successfully created.")

        return super().form_valid(form)


class SchoolDetailView(DetailView):
    model = School
    template_name = 'schools/details.html'
    context_object_name = 'school'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        school = context['school']

        # Initialize coordinates and bbox
        lat, lon = None, None
        bbox = None

        if school.location:
            try:
                lat_str, lon_str = school.location.split(',', 1)
                lat = float(lat_str.strip())
                lon = float(lon_str.strip())

                # Validate coordinate ranges
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    # Precompute bbox with 6 decimal places
                    bbox = {
                        'min_lon': round(lon - 0.005, 6),
                        'min_lat': round(lat - 0.003, 6),
                        'max_lon': round(lon + 0.005, 6),
                        'max_lat': round(lat + 0.003, 6),
                    }
                else:
                    context['location_error'] = "Invalid latitude or longitude values."
            except (ValueError, AttributeError):
                context['location_error'] = "Invalid location format. Expected 'lat,lon'."
        else:
            context['location_error'] = "No location data available."

        context["lat"] = lat
        context["lon"] = lon
        context["bbox"] = bbox
        context['educational_levels'] = school.educational_levels.all()
        context['types'] = school.type.all()
        context['platforms'] = school.platforms.all()
        context['platform_profiles'] = PlatformProfile.objects.filter(school=school)
        context['title'] = "School Information"
        context['active'] = "active"
        context['page_name'] = "school"

        if school.cover_image:
            context['cover_image_url'] = self.request.build_absolute_uri(school.cover_image.url)

        rec_qs = School.objects.exclude(id=school.id)
        filters = Q()
        if school.educational_levels.exists():
            filters |= Q(educational_levels__in=school.educational_levels.all())
        if school.type.exists():
            filters |= Q(type__in=school.type.all())
        if school.location:
            filters |= Q(location=school.location)

        context['related_items'] = rec_qs.filter(filters).distinct()[:6]
        return context
    

class SchoolListView(ListView):
    template_name = 'schools/index.html'
    model = School
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Schools"
        context["active"] = "active"
        return context