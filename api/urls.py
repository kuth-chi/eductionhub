"""
 api/urls.py
 handle api endpoint
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views.school_type_api import SchoolTypeViewSet
from api.views.schools_api import SchoolAPIView, SchoolViewSet

app_name = "api"

router = DefaultRouter()

router.register(r'schools', SchoolViewSet, basename="schools")
router.register(r'school-types', SchoolTypeViewSet, basename="school-types")

urlpatterns = [
    path('', include(router.urls)),
    path('schools-list/', SchoolAPIView.as_view(), name="schools-view"),
]
