import os
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from schools.models import schoolsModel

@receiver(post_save, sender=schoolsModel.School)
def delete_old_logo_on_update(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old_logo = sender.objects.get(pk=instance.pk).logo
    except sender.DoesNotExist:
        return
    
    if old_logo and old_logo != instance.logo:
        if os.path.isfile(old_logo.path):
            old_logo.delete(save=False)
            
@receiver(post_delete, sender=schoolsModel.School)
def delete_logo_on_delete(sender, instance, **kwargs):
    if instance.logo:
        if os.path.isfile(instance.logo.path):
            instance.logo.delete(save=False)