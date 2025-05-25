from django.urls import path
from schools.data import get_school_type_api, get_schools_list_data
from schools.views import base

app_name = "schools"

urlpatterns = [
    path("", base.SchoolListView.as_view(), name="index"),
    path("create/", base.SchoolCreateView.as_view(), name="school_creation_form"),
    path("<int:pk>/", base.SchoolDetailView.as_view(), name="school-detail"),
]
