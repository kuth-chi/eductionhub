"""
 api/urls.py
 handle api endpoint
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views.branchs_viewsets import SchoolBranchViewSet
from api.views.user.profile_viewset import ProfileViewSet
from api.views.school_type_api import SchoolTypeViewSet
from api.views.platform_api import PlatformViewSet, PlatformProfileViewSet
from api.views.location_api import (
    CountryViewSet,
    StateViewSet,
    CityViewSet,
    VillageViewSet,
)
from api.views.schools_api import SchoolAPIView, SchoolViewSet
from api.views.schools_viewsets import (
    EducationalLevelViewSet,
    CollegeViewSet,
    MajorViewSet,
    EducationDegreeViewSet,
    SchoolDegreeOfferingViewSet,
    SchoolCollegeAssociationViewSet,
    SchoolMajorOfferingViewSet,
    FieldOfStudyViewSet,
    ScholarshipViewSet,
    ScholarshipTypeViewSet,
    SchoolScholarshipViewSet,
    SchoolCustomizeButtonViewSet,
    AddressViewSet,
    PhoneContactViewSet,
    SchoolBranchViewSet,
)
from api.views.auth import (
    ActiveSessionsView,
    CookieTokenObtainPairView,
    LogoutView,
    SocialLoginJWTView,
    AuthStatusView,
    csrf_token_view,
)
from api.views.upload_views import upload_file
from api.utils.client_ip import client_ip_info

app_name = "api"

router = DefaultRouter()

router.register(r"schools", SchoolViewSet, basename="schools")
router.register(r"school-types", SchoolTypeViewSet, basename="school-types")
router.register(r"platforms", PlatformViewSet, basename="platforms")
router.register(
    r"platform-profiles", PlatformProfileViewSet, basename="platform-profiles"
)
router.register(r"countries", CountryViewSet, basename="countries")
router.register(r"states", StateViewSet, basename="states")
router.register(r"cities", CityViewSet, basename="cities")
router.register(r"villages", VillageViewSet, basename="villages")
router.register(
    r"educational-levels", EducationalLevelViewSet, basename="educational-levels"
)
router.register(r"profiles", ProfileViewSet)
router.register(r"colleges", CollegeViewSet, basename="colleges")
router.register(r"majors", MajorViewSet, basename="majors")
router.register(r"degrees", EducationDegreeViewSet, basename="degrees")
router.register(r"branches", SchoolBranchViewSet, basename="branches")
router.register(
    r"degree-offerings", SchoolDegreeOfferingViewSet, basename="degree-offerings"
)
router.register(
    r"college-associations",
    SchoolCollegeAssociationViewSet,
    basename="college-associations",
)
router.register(
    r"major-offerings", SchoolMajorOfferingViewSet, basename="major-offerings"
)
router.register(r"fields-of-study", FieldOfStudyViewSet, basename="fields-of-study")
router.register(r"scholarships", ScholarshipViewSet, basename="scholarships")
router.register(
    r"scholarship-types", ScholarshipTypeViewSet, basename="scholarship-types"
)
router.register(
    r"school-scholarships", SchoolScholarshipViewSet, basename="school-scholarships"
)
router.register(
    r"custom-buttons", SchoolCustomizeButtonViewSet, basename="custom-buttons"
)
router.register(r"addresses", AddressViewSet, basename="addresses")
router.register(r"contacts", PhoneContactViewSet, basename="contacts")

urlpatterns = [
    path("", include(router.urls)),
    path("schools-list/", SchoolAPIView.as_view(), name="schools-view"),
    path("social-jwt/", SocialLoginJWTView.as_view(), name="social-jwt"),
    path("token/", CookieTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("auth-status/", AuthStatusView.as_view(), name="auth-status"),
    path('active-sessions/', ActiveSessionsView.as_view(), name='active-sessions'),
    path('utils/client-ip/', client_ip_info, name='client-ip-info'),
    path('csrf/', csrf_token_view, name='csrf-token'),
    path("upload/", upload_file, name="upload"),
]
