""" Ads/url.py """
from django.urls import path
from ads import views

app_name = "ads"

urlpatterns = [
    path("", views.AdsDashboardView.as_view() , name="dashboard"),
]