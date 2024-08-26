""" User profile model """
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext as _
# Create your models here.

def user_directory_path(instance, filename):
    """Generate file path for new profile image"""
    # File will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return f'user_{instance.user.username}/{filename}'

class User(AbstractUser):
    """ Abstract django user model"""
    pass


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
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def delete(self, *args, **kwargs):
        # Ensure the file is deleted when the profile is deleted
        self.photo.delete(save=False)
        super().delete(*args, **kwargs)
        
    
