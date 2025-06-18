from django.shortcuts import get_object_or_404, render, redirect
import qrcode
import io
import logging
import base64
from django.views import View
from django.urls import reverse
from schools.models.OnlineProfile import Platform
from schools.models.schoolsModel import School
from user.models import Letter, Profile, ProfileContact
from user.models import Experience
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required
from user.views.experience import ExperienceObject 
from django.contrib import messages 

logger = logging.getLogger(__name__)

# @login_required
class ProfileView(View):
    def get(self, request, qr=None):
        template_name = 'profile/index.html'
        page_title = _("Profile")

        # user_profile = Profile.objects.get(user=request.user)
        user_profile = get_object_or_404(Profile, user=request.user)

        experience_object = ExperienceObject(user=user_profile)
        experiences = experience_object.get_by_user()
        letter = get_object_or_404(Letter, user=request.user)

        # Build absolute public profile URL
        public_profile_url = request.build_absolute_uri(
            reverse('profiles:public_profile', kwargs={'id': user_profile.uuid})
        )

        # Generate QR code
        qr_image = qrcode.make(public_profile_url)
        buffered = io.BytesIO()
        qr_image.save(buffered, format="PNG")
        qr_code_base64 = base64.b64encode(buffered.getvalue()).decode()
        privacy_choices = ProfileContact.PrivacyChoices.choices 
        contact_profiles = ProfileContact.objects.filter(profile__user=request.user)

        platforms = Platform.objects.all()

        context = {
            "Title": page_title,
            "Header": "Profile",
            "experiences": experiences,
            "profile": user_profile,
            "letter": letter.content,
            "contact_profiles": ProfileContact.objects.filter(profile__user=request.user, privacy=0),
            "qr_code_base64": qr_code_base64,
            "public_profile_url": public_profile_url,
            "privacy_choices": privacy_choices,
            "contact_profiles": contact_profiles,
            "platforms": platforms,
        }

        return render(request, template_name, context)
    
    def save_experience(self, request):
        """
        Save or update an experience based on the provided request data.
        """
        if request.method == 'POST':
            
            user = request.user
            experience_data = {
                'title': request.POST.get('title'),
                'organization': request.POST.get('company'),
                'start_date': request.POST.get('start_date'),
                'end_date': request.POST.get('end_date'),
                'responsibilities': request.POST.get('description'),
            }
            
            # Initialize the ExperienceObject with the user and experience data
            experience_object = ExperienceObject(user=user, experience_request=experience_data)

            # Check if there's an 'uuid' to update an existing experience
            experience_id = request.POST.get('uuid')  # Assuming 'uuid' is the identifier for updating
            
            if experience_id:  
                # Update the experience if an ID is provided
                updated_experience = experience_object.update(experience_id)
                if updated_experience:
                    return redirect('profiles:profile')
                else:
                    pass
            else:
                
                new_experience = experience_object.create()
                if new_experience:
                    return redirect('profiles:profile') 
        
        return redirect('profiles:profile')

    def save_education(self, request, education):
        """
        A placeholder for saving education data, if you need it.
        """
        pass

class PublicProfileView(View):
    def get(self, request, id):
        logger.info(f"Accessing public profile with id={id}")
        template_name = 'profile/public.html'
        page_title = _("Profile")

        user_profile = get_object_or_404(Profile, uuid=id)
        experience_object = ExperienceObject(user=user_profile)
        experiences = experience_object.get_by_user()
        letter = get_object_or_404(Letter, user=user_profile.user)

        full_name = "unknown"
        if user_profile.user.first_name and user_profile.user.last_name:
            full_name = f"{user_profile.user.first_name} {user_profile.user.last_name}"

        context = {
            "Title": page_title + " " + full_name,
            "Header": "Profile",
            "experiences": experiences,
            "letter": letter.content,
            "contact_profiles": ProfileContact.objects.filter(profile__user=user_profile.user, privacy=0),
            "profile": user_profile, 
            'platforms': Platform.objects.all()
        }

        return render(request, template_name, context)
    

class EditContactView(View):
    def post(self, request, uuid):
        contact = get_object_or_404(ProfileContact, uuid=uuid, profile__user=request.user)

        contact.profile_url = request.POST.get("profile_url")
        contact.username = request.POST.get("username")
        contact.privacy = request.POST.get("privacy")
        contact.save()

        messages.success(request, "Contact updated!")
        return redirect("profiles:profile")
    
class AddContactView(View):
    def post(self, request):
        platform_id = request.POST.get("platform")
        profile_url = request.POST.get("profile_url")
        username = request.POST.get("username")
        privacy = request.POST.get("privacy")

        platform = get_object_or_404(Platform, id=platform_id)

        ProfileContact.objects.create(
            profile=request.user.profile,
            platform=platform,
            profile_url=profile_url,
            username=username,
            privacy=privacy,
        )

        messages.success(request, "Contact added!")
        return redirect("profiles:profile")