from django.urls import path

from user.views.base import token_view, verify_token_view
from .views import user_view, profile

urlpatterns = [
    path('register/', user_view.user_register, name='register'),
    path('login/', user_view.user_login, name='login'),
    path('logout/', user_view.user_logout, name='logout'),
    path('token/', token_view),
    path('verify-token/', verify_token_view),
    path('', profile.ProfileView.as_view(), name='profile'),
    path('<uuid:id>/', profile.PublicProfileView.as_view(), name='public_profile'),
    path('contact/edit/<uuid:uuid>/', profile.EditContactView.as_view(), name='edit_contact'),
    path('contact/add/', profile.AddContactView.as_view(), name='add_contact'),


]
