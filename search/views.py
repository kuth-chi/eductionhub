from django.db.models import Q
from django.views.generic import ListView
from schools.models.school import School
import logging

logger = logging.getLogger(__name__)

class SchoolListSearchView(ListView):
    template_name = 'pages/search.html'
    model = School
    paginate_by = 20
    context_object_name = 'schools'  # optional: for clarity in templates

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("q")

        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(local_name__icontains=query) |
                Q(short_name__icontains=query) |
                Q(code__icontains=query) |
                Q(description__icontains=query) |
                Q(founder__icontains=query) |
                Q(president__icontains=query) |
                Q(location__icontains=query) |
                Q(motto__icontains=query)
            ).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "")
        context["page_title"] = f"'{query}'" if query else "Search for Schools"
        context["active"] = "active"
        context["search_count"] = self.get_queryset().count()
        context["query"] = query  # so you can prefill the search box in the template
        return context