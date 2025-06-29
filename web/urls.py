from django.urls import path
from .views import about_us, our_privacy, terms_conditions

app_name = "web"

urlpatterns = [
    path("about-us/", about_us, name="about_us"),
    path("privacy-policy/", our_privacy, name="about_us"),
    path("terms-conditions/", terms_conditions, name="about_us"),
]