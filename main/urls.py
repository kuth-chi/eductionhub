from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from oauth2_provider import urls as oauth2_urls
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from user.views import base
from django.views.i18n import set_language
from rest_framework import permissions
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView)


schema_view = get_schema_view(
    openapi.Info(
        title="Auth Server API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@authserver.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('super-user/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/', include("api.urls", namespace="api")),
    # swagger
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    # allauth
    path('accounts/', include('allauth.urls')),
    
]

urlpatterns += i18n_patterns(
    # oauth2
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path("", base.index, name="home"),
    path("scholarships/", base.scholarship, name="scholarships"),
    path("ads/", include("ads.urls"), name="ads"),
    path('school/type/<str:type>/', base.index, name='home_type'),
    # app urls
    path("profiles/", include("user.urls", namespace="profiles")),
    path("search/", include("search.urls", namespace="search")),
    path("admin-edu/", include("administrator.urls", namespace="administrator")),
    path("organizations/", include("organization.urls", namespace="organization")),
    path("schools/", include("schools.urls", namespace="schools")),
    path("app/", include("health_check.urls", namespace="health_check")),
    path("pages/", include("web.urls", namespace="web")),
    # language switcher
    path('set_language/', set_language, name='set_language'),
)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Rosetta for translation
if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += [path('rosetta/', include('rosetta.urls'))]
