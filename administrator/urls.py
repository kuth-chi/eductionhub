""" Administrator URLs.py"""
from django.urls import path, include
from administrator import views

app_name = "administrator"

urlpatterns = [
    path("", views.AdminIndexView.as_view(), name="dashboard"),
    path("ads-manager/", include("ads.urls", namespace="ads")),
]
