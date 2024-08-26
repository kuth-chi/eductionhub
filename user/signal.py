""" Signal automatically create objects from models """
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
# Internal app modules import
from .models import User, Profile


@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    """ Create or update a profile base on the given instance"""
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()
        
@receiver(post_delete, sender=Profile)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """ Deletes file from filesystem when corresponding `Profile` object is deleted. """
    if instance.photo:
        instance.photo.delete(save=False)
    
@receiver(post_delete, sender=User)
def auto_delete_profile_on_delete_user(sender, instance, **kwargs):
    """ Deletes `Profile` object when corresponding `User` object is deleted. """
    try:
        instance.profile.delete()
    except Profile.DoesNotExist:
        pass
