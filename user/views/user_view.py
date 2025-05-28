import logging
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
                return redirect('accounts:login')
    else:
        form = RegisterForm()
    return render(request, template_name)


def user_login(request):
    template_name = 'accounts/sign-in.html'
    
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            Profile.objects.get_or_create(user=user)
            login(request, user)
            
            # Retrieve the next URL from the request
            next_url = request.GET.get('next')
            if not next_url:
                return redirect('/')
            
            # Make sure the next URL is not the login page itself
            if next_url.startswith('/accounts/login'):
                next_url = '/'
            
            # Add the code and state to the redirect URL if present
            code = request.COOKIES.get('authorization_code')
            state = request.COOKIES.get('state')
            if code and state:
                # Ensure the full URL for the Resource Server
                if not next_url.startswith('http'):
                    next_url = f"http://localhost:8100{next_url}"
                next_url = f"{next_url}?code={code}&state={state}"
            
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid Username or Password')
    
    return render(request, template_name)


# def user_logout(request):
def user_logout(request):
    logout(request)
    return redirect('accounts:login')