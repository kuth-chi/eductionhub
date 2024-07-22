from django.urls import path
from .views import user_view

urlpatterns = [
    path('register/', user_view.user_register, name='register'),
    path('login/', user_view.user_login, name='login'),
    path('logout/', user_view.user_logout, name='logout'),
]
