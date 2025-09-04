"""
 api/urls.py
 handle api endpoint
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.debug_views import debug_cookies_backend
from api.utils.client_ip import client_ip_info
from api.views.ads_manager import (AdClickViewSet, AdImpressionViewSet,
                                   AdManagerViewSet, AdPlacementViewSet,
                                   AdSpaceViewSet, AdTypeViewSet,
                                   UserBehaviorViewSet)
from api.views.ads_manager import UserProfileViewSet as AdsUserProfileViewSet
from api.views.auth.auth_viewset import (ActiveSessionsView, AuthStatusView,
                                         CookieTokenObtainPairView,
                                         CustomTokenRefreshView, LogoutView,
                                         SocialLoginJWTView, csrf_token_view)
from api.views.auth.social_auth_complete import (FacebookSocialLoginView,
                                                 GoogleSocialLoginView,
                                                 TelegramSocialLoginView)
from api.views.auth.social_auth_viewset import GoogleLogin
from api.views.location_api import (CityViewSet, CountryViewSet, StateViewSet,
                                    VillageViewSet)
from api.views.organizations.founder_viewset import FounderViewSet
from api.views.organizations.industry_viewset import IndustryViewSet
from api.views.organizations.organization_viewset import OrganizationViewSet
from api.views.platform_profile_viewset import (PlatformProfileViewSet,
                                                PlatformViewSet)
from api.views.schools.branches_viewsets import SchoolBranchViewSet
from api.views.schools.colleges_viewset import CollegeViewSet
from api.views.schools.degrees_viewset import EducationDegreeViewSet
from api.views.schools.document_requirement_viewset import \
    MajorDocumentRequirementViewSet
from api.views.schools.education_level_viewsets import EducationalLevelViewSet
from api.views.schools.majors_viewset import MajorViewSet
from api.views.schools.qualification_candidate_viewset import \
    QualificationCandidateViewSet
from api.views.schools.school_type_api import SchoolTypeViewSet
from api.views.schools.schools_viewset import SchoolAPIView, SchoolViewSet
from api.views.schools.schools_viewsets import (
    AddressViewSet, FieldOfStudyViewSet, ScholarshipTypeViewSet,
    ScholarshipViewSet, SchoolBranchContactInfoViewSet,
    SchoolCollegeAssociationViewSet, SchoolCustomizeButtonViewSet,
    SchoolDegreeOfferingViewSet, SchoolMajorOfferingViewSet,
    SchoolScholarshipViewSet)
from api.views.upload_views import upload_file
from api.views.user.profile_viewset import ProfileViewSet

app_name = "api"

router = DefaultRouter()

router.register(r"schools", SchoolViewSet, basename="schools")
router.register(r'industries', IndustryViewSet, basename="industries")
router.register(r'founders', FounderViewSet, basename="founders")
router.register(r"organizations", OrganizationViewSet,
                basename="organizations")
router.register(r"school-types", SchoolTypeViewSet, basename="school-types")
router.register(r"platforms", PlatformViewSet, basename="platforms")
router.register(r"platform-profiles", PlatformProfileViewSet,
                basename="platform-profiles")
router.register(r"countries", CountryViewSet, basename="countries")
router.register(r"states", StateViewSet, basename="states")
router.register(r"cities", CityViewSet, basename="cities")
router.register(r"villages", VillageViewSet, basename="villages")
router.register(r"educational-levels", EducationalLevelViewSet,
                basename="educational-levels")
router.register(r"profiles", ProfileViewSet)
router.register(r"majors", MajorViewSet, basename="majors")
router.register(r"major-qualifications",
                QualificationCandidateViewSet, basename="major-qualifications")
router.register(r"major-document-requirements",
                MajorDocumentRequirementViewSet, basename="major-document-requirements")
router.register(r"colleges", CollegeViewSet, basename="colleges")
router.register(r"degrees", EducationDegreeViewSet, basename="degrees")
router.register(r"school-branches", SchoolBranchViewSet, basename="branches")
router.register(r"degree-offerings", SchoolDegreeOfferingViewSet,
                basename="degree-offerings")
router.register(r"college-associations",
                SchoolCollegeAssociationViewSet, basename="college-associations")
router.register(r"major-offerings", SchoolMajorOfferingViewSet,
                basename="major-offerings")
router.register(r"fields-of-study", FieldOfStudyViewSet,
                basename="fields-of-study")
router.register(r"scholarships", ScholarshipViewSet, basename="scholarships")
router.register(r"scholarship-types", ScholarshipTypeViewSet,
                basename="scholarship-types")
router.register(r"school-scholarships", SchoolScholarshipViewSet,
                basename="school-scholarships")
router.register(r"custom-buttons", SchoolCustomizeButtonViewSet,
                basename="custom-buttons")
router.register(r"addresses", AddressViewSet, basename="addresses")
router.register(r"school-contacts",
                SchoolBranchContactInfoViewSet, basename="contacts")

# Ads Manager routes
router.register(r"ad-types", AdTypeViewSet, basename="ad-types")
router.register(r"ad-spaces", AdSpaceViewSet, basename="ad-spaces")
router.register(r"ad-campaigns", AdManagerViewSet, basename="ad-campaigns")
router.register(r"ad-placements", AdPlacementViewSet, basename="ad-placements")
router.register(r"ad-impressions", AdImpressionViewSet,
                basename="ad-impressions")
router.register(r"ad-clicks", AdClickViewSet, basename="ad-clicks")
router.register(r"ads-user-profiles", AdsUserProfileViewSet,
                basename="ads-user-profiles")
router.register(r"user-behavior", UserBehaviorViewSet,
                basename="user-behavior")

urlpatterns = [
    path("", include(router.urls)),
    # dj-rest-auth endpoints (complete authentication)
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),

    # Social authentication endpoints (dj-rest-auth + allauth)
    path('auth/google/', GoogleSocialLoginView.as_view(),
         name='google_social_login'),
    path('auth/facebook/', FacebookSocialLoginView.as_view(),
         name='facebook_social_login'),
    path('auth/telegram/', TelegramSocialLoginView.as_view(),
         name='telegram_social_login'),

    # Legacy endpoints (for backward compatibility)
    path('auth/google/legacy/', GoogleLogin.as_view(), name='google_login_legacy'),

    # Custom authentication endpoints
    path("social-jwt/", SocialLoginJWTView.as_view(), name="social-jwt"),
    path("token/", CookieTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("auth-status/", AuthStatusView.as_view(), name="auth-status"),
    path('active-sessions/', ActiveSessionsView.as_view(), name='active-sessions'),
    path('csrf/', csrf_token_view, name='csrf-token'),

    # Other endpoints
    path("schools-list/", SchoolAPIView.as_view(), name="schools-view"),
    path('utils/client-ip/', client_ip_info, name='client-ip-info'),
    path("upload/", upload_file, name="upload"),

    # Debug endpoint for production troubleshooting
    path('debug/cookies/', debug_cookies_backend, name='debug-cookies-backend'),
]
