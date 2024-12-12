"""
 api/urls.py
 handle api endpoint
"""
from django.urls import path, include
from rest_framework.routers import SimpleRouter

from api.views.schools_api import SchoolAPIView, SchoolViewSet

app_name = "api"

router = SimpleRouter()

router.register(r'schools', SchoolViewSet, basename="schools")

urlpatterns = [
    path('', include(router.urls)),
    path('schools-list/', SchoolAPIView.as_view(), name="schools-view"),
]
