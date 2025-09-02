from django.urls import path

from .views import about_us, our_privacy, terms_conditions

app_name = "web"

urlpatterns = [
    path("about-us/", about_us, name="about_us"),
    path("privacy/", our_privacy, name="privacy_policy"),
    path("terms-conditions/", terms_conditions, name="terms_conditions"),
]
