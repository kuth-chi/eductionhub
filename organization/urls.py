""" Organization App Engine URLs reference """
from django.urls import path
from organization import views

app_name = 'organization'
urlpatterns = [
    path("", views.OrganizationDashboardView.as_view(), name="dashboard"),
]