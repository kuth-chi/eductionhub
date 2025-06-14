from django.urls import path
from search.views import SchoolListSearchView

app_name = "search"

urlpatterns = [
    path("", SchoolListSearchView.as_view(), name="search_schools"),
]
