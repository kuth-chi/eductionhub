import logging
import time
from django.core.cache import cache
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from user.models import User, Profile
from user.forms.user_forms import RegisterForm, CustomerAuthenticationForm

# Create your views here.
def user_register(request):
    template_name = "accounts/register.html"
    
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        
        # Check if password and confirm password match
        if not username or not password or not confirm_password:
            messages.error(request, "Please fill in all fields")
        elif password != confirm_password:
            messages.warning(request, "Passwords do not match")
        else:
            if User.objects.filter(username=username).exists():
                messages.warning(request, "Email already exists")
            else:
                user = User.objects.create_user(username=username, password=password)
                user.save()
                messages.success(request, "Account created successfully")
                return redirect('profiles:login')
    else:
        form = RegisterForm()
    return render(request, template_name)



def user_login(request):
    template_name = 'accounts/sign-in.html'

    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        # Rate-limiting: get failed attempts from cache
        cache_key = f"login_attempts_{username}"
        attempts = cache.get(cache_key, 0)

        # Introduce delay: 1 + 1 * attempts seconds
        time.sleep(1 + attempts)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Reset the attempt counter on successful login
            cache.delete(cache_key)

            Profile.objects.get_or_create(user=user)
            login(request, user)

            next_url = request.GET.get('next')
            if not next_url or next_url.startswith('/accounts/login'):
                next_url = '/'

            code = request.COOKIES.get('authorization_code')
            state = request.COOKIES.get('state')
            if code and state:
                if not next_url.startswith('http'):
                    next_url = f"http://localhost:8100{next_url}"
                next_url = f"{next_url}?code={code}&state={state}"

            return redirect(next_url)
        else:
            # Increment failed attempts
            cache.set(cache_key, attempts + 1, timeout=300)  # expire after 5 minutes
            messages.error(request, 'Invalid Username or Password')

    return render(request, template_name)


# def user_logout(request):
def user_logout(request):
    logout(request)
    return redirect('profiles:login')