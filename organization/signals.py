
import os
from django.db.models.signals import post_delete
from django.dispatch import receiver
from organization import models


@receiver(post_delete, sender=models.base.Organization)
def delete_logo_on_delete(sender, instance, **kwargs):
    if instance.logo:
        if os.path.isfile(instance.logo.path):
            instance.logo.delete(save=False)