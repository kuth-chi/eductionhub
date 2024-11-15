from django.urls import path
from schools.views import base

app_name = "schools"

urlpatterns = [
    path("", base.IndexView.as_view(), name="index")
]
