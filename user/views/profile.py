import qrcode
import io
import logging
import base64
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.views.generic.edit import CreateView
from django.urls import reverse, reverse_lazy
from schools.models.OnlineProfile import Platform
from shared.helper import QRCodeGenerator
from user.models import Letter, Profile, ProfileContact
from django.utils.translation import gettext as _
from user.views.experience import ExperienceObject 
from django.contrib import messages

logger = logging.getLogger(__name__)

# @login_required
class ProfileDetailView(DetailView):
    model = Profile
    template_name = 'profile/index.html'
    context_object_name = 'profile'

    def get_object(self):
        # This ensures the Profile exists for the current user, or raises a 404
        return get_object_or_404(Profile, user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_profile = self.object
        experience_object = ExperienceObject(user=user_profile)
        experiences = experience_object.get_by_user()

        # --- CHANGE HERE: Handle nullable Letter object ---
        letter_obj = Letter.objects.filter(user=self.request.user).first()
        letter_content = letter_obj.content if letter_obj else _("No letter content available.")
        # ----------------------------------------------------

        # Build public profile URL
        public_profile_url = self.request.build_absolute_uri(
            reverse('profiles:public_profile', kwargs={'id': user_profile.uuid})
        )

        # Generate QR Code
        try:
            qr_image = qrcode.make(public_profile_url)
            buffered = io.BytesIO()
            qr_image.save(buffered, format="PNG")
            qr_code_base64 = base64.b64encode(buffered.getvalue()).decode()
        except Exception as e:
            qr_code_base64 = None
            print(f"Error generating QR code: {e}") # Log the error for debugging


        # Contacts and platforms
        contact_profiles = ProfileContact.objects.filter(profile__user=self.request.user)
        privacy_choices = ProfileContact.PrivacyChoices.choices
        platforms = Platform.objects.all()

        # Add to context
        context.update({
            "Title": _("Profile"),
            "Header": "Profile",
            "experiences": experiences,
            "letter": letter_content, # Use the potentially empty or default letter_content
            "contact_profiles": contact_profiles.filter(privacy=0), # Filter for public contacts
            "qr_code_base64": qr_code_base64,
            "public_profile_url": public_profile_url,
            "privacy_choices": privacy_choices,
            "contact_profiles": contact_profiles, # This will include all contacts, public or not. You might want to adjust how you use this in the template if you display private ones.
            "platforms": platforms,
            "now": timezone.now(),
        })
        return context

    def post(self, request, *args, **kwargs):
        """
        Optional POST handler for experience saving
        """
        if request.POST.get("form_type") == "experience":
            return self.save_experience(request)
        return redirect('profiles:profile')

    def save_experience(self, request):
        user = request.user
        experience_data = {
            'title': request.POST.get('title'),
            'organization': request.POST.get('company'),
            'start_date': request.POST.get('start_date'),
            'end_date': request.POST.get('end_date'),
            'responsibilities': request.POST.get('description'),
        }

        experience_object = ExperienceObject(user=user, experience_request=experience_data)
        experience_id = request.POST.get('uuid')

        if experience_id:
            updated_experience = experience_object.update(experience_id)
            if updated_experience:
                return redirect('profiles:profile')
        else:
            new_experience = experience_object.create()
            if new_experience:
                return redirect('profiles:profile')

        return redirect('profiles:profile')

class PublicProfileDetailView(DetailView):
    model = Profile
    template_name = 'profile/public.html'
    context_object_name = 'profile'
    pk_url_kwarg = 'id'  # This maps 'id' from the URL to the object's 'pk' (uuid in this case)

    def get_object(self, queryset=None):
        uuid = self.kwargs.get(self.pk_url_kwarg)
        logger.info(f"Accessing public profile with id={uuid}")
        return get_object_or_404(Profile, uuid=uuid)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_profile = self.object
        experience_object = ExperienceObject(user=user_profile)
        experiences = experience_object.get_by_user()
        letter_obj = Letter.objects.filter(user=user_profile.user).first()
        letter_content = letter_obj.content if letter_obj else _("No letter content available.")
    

        full_name = "unknown"
        if user_profile.user.first_name and user_profile.user.last_name:
            full_name = f"{user_profile.user.first_name} {user_profile.user.last_name}"

        context.update({
            "Title": _("Profile") + " " + full_name,
            "Header": "Profile",
            "experiences": experiences,
            "letter": letter_content,
            "contact_profiles": ProfileContact.objects.filter(profile__user=user_profile.user, privacy=0),
            "platforms": Platform.objects.all(),
        })

        return context
    

class EditContactView(UpdateView):
    model = ProfileContact
    fields = ['profile_url', 'username', 'privacy']
    template_name = 'profile/edit_contact.html'
    context_object_name = 'contact'
    pk_url_kwarg = 'uuid'  # Keep for clarity

    def get_object(self, queryset=None):
        """Fetch the object by UUID and ensure the contact belongs to the current user."""
        uuid = self.kwargs.get(self.pk_url_kwarg)
        contact = get_object_or_404(ProfileContact, uuid=uuid, profile__user=self.request.user)
        return contact

    def form_valid(self, form):
        messages.success(self.request, _("Contact updated!"))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("profiles:profile")
    
class AddContactView(CreateView):
    model = ProfileContact
    fields = ['platform', 'profile_url', 'username', 'privacy']
    template_name = 'profile/add_contact.html'  # Optional if rendering via GET

    def form_valid(self, form):
        platform_id = self.request.POST.get("platform")
        platform = get_object_or_404(Platform, id=platform_id)

        # Set fields that are not coming from the form
        form.instance.profile = self.request.user.profile
        form.instance.platform = platform

        messages.success(self.request, _("Contact added!"))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("profiles:profile")

    def post(self, request, *args, **kwargs):
        # Prevent duplicate platform selection logic, if needed, could go here
        """
        Handles POST requests for adding a new profile contact.
        
        Delegates form processing to the parent class. Intended as an extension point for additional logic, such as preventing duplicate platform selection.
        """
        return super().post(request, *args, **kwargs)
    
# Beta testing
@login_required
def profile_beta(request):
    """
    Render the beta version of the profile page with a static title and content.
    """
    template_name = "profile/profile-beta.html"

    if not request.user.is_authenticated:
        return redirect('profiles:login')
    user = request.user
    profile = get_object_or_404(Profile, user=user)

    # Build public profile URL
    public_profile_url = request.build_absolute_uri(
        reverse('profiles:public_profile', kwargs={'id': profile.uuid})
    )

    # Generate QR Code
    qr_generator = QRCodeGenerator(public_profile_url)
    qr_code_base64 = qr_generator.generate_base64()

    # Contacts and platforms
    contact_profiles = ProfileContact.objects.filter(profile__user=user)
    privacy_choices = ProfileContact.PrivacyChoices.choices
    platforms = Platform.objects.all()

    # Experiences
    # experience_object = ExperienceObject(user=user)
    # experiences = experience_object.get_by_user()
    letter_obj = Letter.objects.filter(user=user).first()
    letter_content = letter_obj.content if letter_obj else _("No letter content available.")
    


    context = {
        "title":  _("Profile"),
        "page_title": "Beta profile",
        "content": "Profile Beta content",
        "profile": profile,
        "Header": "Profile",
        # "experiences": experiences,
        "letter": letter_content,
        "contact_profiles": contact_profiles.filter(privacy=0),
        "qr_code_base64": qr_code_base64,
        "public_profile_url": public_profile_url,
        "privacy_choices": privacy_choices,
        "contact_profiles": contact_profiles,
        "platforms": platforms,
        "now": timezone.now(),
    }
    return render(request, template_name, context)