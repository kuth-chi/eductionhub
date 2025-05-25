""" User profile model """
import mimetypes
import uuid
import pytz
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext as _
from django.core.files.storage import default_storage
from schools.models.OnlineProfile import Platform
from schools.models.schoolsModel import School
from organization.models import Organization
# Create your models here.


def user_directory_path(instance, filename):
    """Generate file path for new profile image"""
    # File will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return f'user_{instance.user.username}/{filename}'


class User(AbstractUser):
    """ Abstract django user model"""
    pass

class Attachment(models.Model):
    file = models.FileField(upload_to="attachments/", verbose_name=_("file"))
    name = models.CharField(max_length=255, blank=True, verbose_name=_("file name"))
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name=_("uploaded at"))
    content_type = models.CharField(max_length=100, blank=True, verbose_name=_("content type"))

    def __str__(self):
        return self.name or str(self.file)

    def save(self, *args, **kwargs):
        if not self.content_type and self.file:
            # Automatically set the content type based on file extension
            import mimetypes
            content_type, _ = mimetypes.guess_type(self.file.name)
            if content_type:
                self.content_type = content_type
            else:
                self.content_type = 'application/octet-stream'  

        if not self.name:
            self.name = self.file.name.split("/")[-1] 
        
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if not self.is_used():
            if self.file:
                if default_storage.exists(self.file.name):
                    default_storage.delete(self.file.name)
        
        super().delete(*args, **kwargs)

    def is_used(self):
        # Check if the attachment is being used in any other models (e.g., Education, Experience, etc.)
        from django.db.models import Q
        return self.education_set.exists() or self.experience_set.exists()

    class Meta:
        verbose_name = _("attachment")
        verbose_name_plural = _("attachments")

class Letter(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    class Meta:
        ordering = ["-created_date"]
        verbose_name = _("letter")
        verbose_name_plural = _("letters")

class Profile(models.Model):
    """ Create profile model instance django user model"""
    uuid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)
    user = models.OneToOneField(User, db_index=True, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to=user_directory_path, blank=True, null=True)
    GENDER_CHOICES = [
        ("FEMALE", _("Female")),
        ("MALE", _("Male")),
        ("OTHER", _("Other"))
    ]
    gender = models.CharField(max_length=6, blank=True, choices=GENDER_CHOICES)
    occupation = models.CharField(max_length=75, default="untitled")
    timezone = models.CharField(max_length=100, choices=[(
        tz, tz) for tz in pytz.all_timezones], default='UTC')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    def delete(self, *args, **kwargs):
        # Check if the photo field has an associated file
        if self.photo and self.photo.name:
            self.photo.delete(save=False)
        super().delete(*args, **kwargs)

    def __str__(self):
        user_first_name = self.user.first_name if self.user.first_name else self.user.username
        user_last_name = self.user.last_name if self.user.last_name else ""
        user_name = f"{user_first_name} {user_last_name}"
        return user_name


class Experience(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    responsibilities = models.TextField(verbose_name=_("responsibilities"))
    attachments = models.ManyToManyField("Attachment", blank=True, verbose_name=_("attachments"))

    def __str__(self):
        return f"{self.title} at {self.organization.name}"
    objects = models.Manager()
    class Meta:
        ordering = ["-start_date"]
        verbose_name = _("experience")
        verbose_name_plural = _("experiences")

class Education(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    institution = models.ForeignKey(School, null=True, on_delete=models.CASCADE)
    degree = models.CharField(max_length=100, blank=True, verbose_name=_("degree"))
    start_date = models.DateField(verbose_name=_("start date"))
    end_date = models.DateField(verbose_name=_("end date"))
    description = models.TextField(verbose_name=_("description"))
    attachments = models.ManyToManyField("Attachment", blank=True, verbose_name=_("attachments"))

    def __str__(self):
        return f"{self.degree} at {self.school}"
    objects = models.Manager()
    class Meta:
        ordering = ["-start_date"]
        verbose_name = _("education")
        verbose_name_plural = _("educations")

class Skill(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    level = models.CharField(max_length=100, blank=True, verbose_name=_("level"))
    attachments = models.ManyToManyField("Attachment", blank=True, verbose_name=_("attachments"))

    def __str__(self):
        return self.name
    objects = models.Manager()
    class Meta:
        verbose_name = _("skill")
        verbose_name_plural = _("skills")
        ordering = ["name"]

class Language(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    level = models.CharField(max_length=100, blank=True, verbose_name=_("level"))
    is_native = models.BooleanField(default=False, verbose_name=_("native"))
    attachments = models.ManyToManyField("Attachment", blank=True, verbose_name=_("attachments"))

    def __str__(self):
        return self.name
    objects = models.Manager()
    class Meta:
        verbose_name = _("language")
        verbose_name_plural = _("languages")
        ordering = ["name"]

class Hobby(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name
    objects = models.Manager()
    class Meta:
        verbose_name = _("hobby")
        verbose_name_plural = _("hobbies")
        ordering = ["name"]

class Reference(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100, blank=True, verbose_name=_("position"))
    company = models.ForeignKey(Organization, related_name="references", on_delete=models.SET_NULL, null=True)
    relationship = models.CharField(max_length=100, blank=True, verbose_name=_("relationship"))
    phone = models.CharField(max_length=100, blank=True, verbose_name=_("phone"))
    email = models.EmailField(max_length=100, blank=True, verbose_name=_("email"))
    attachments = models.ManyToManyField("Attachment", blank=True, verbose_name=_("attachments"))

    def __str__(self):
        return self.name
    objects = models.Manager()
    class Meta:
        verbose_name = _("reference")
        verbose_name_plural = _("references")
        ordering = ["name"]


class ProfileContact(models.Model):
    """Represents a profile of a school on a specific online platform"""
    class PrivacyChoices(models.IntegerChoices):
        PUBLIC = 0, 'Public'
        CONNECTED = 1, 'Connected'
        PRIVATE = 2, 'Private'
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="contact_profiles")
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, related_name="contact_profiles_platform")
    profile_url = models.URLField(blank=True, help_text=_("URL of the school's profile on the platform"))
    username = models.CharField(max_length=128, blank=True, help_text=_("Username or handle on the platform"))
    privacy = models.IntegerField(choices=PrivacyChoices.choices, default=PrivacyChoices.PUBLIC)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        if self.profile.user.first_name and self.profile.user.last_name:
            full_name = self.profile.user.first_name + " " + self.profile.user.last_name
        else:
            full_name = self.profile.user.username
        return full_name

    class Meta:
        verbose_name = _("contact profile")
        verbose_name_plural = _("contact profiles")