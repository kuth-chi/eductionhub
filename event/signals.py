"""
Event app signal handlers.

Handles automatic cleanup of old image files when Event instances are updated or deleted.
"""

from django.core.files.storage import default_storage
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist

from event.models import Event


@receiver(pre_save, sender=Event)
def delete_old_event_images_on_change(sender, instance, **kwargs):
    """
    Delete old banner_image and thumbnail_image when they are changed.

    This prevents orphaned files from accumulating in storage when users
    upload new images to replace existing ones.
    """
    if not instance.pk:
        # New instance, no old images to delete
        return

    try:
        old_instance = Event.objects.get(pk=instance.pk)
    except ObjectDoesNotExist: 
        # Instance doesn't exist yet, nothing to delete
        return

    # Check and delete old banner_image if changed
    if old_instance.banner_image and old_instance.banner_image != instance.banner_image:
        if default_storage.exists(old_instance.banner_image.name):
            default_storage.delete(old_instance.banner_image.name)

    # Check and delete old thumbnail_image if changed
    if old_instance.thumbnail_image and old_instance.thumbnail_image != instance.thumbnail_image:
        if default_storage.exists(old_instance.thumbnail_image.name):
            default_storage.delete(old_instance.thumbnail_image.name)


@receiver(post_delete, sender=Event)
def delete_event_images_on_delete(sender, instance, **kwargs):
    """
    Delete banner_image and thumbnail_image when Event instance is deleted.

    This ensures that image files are removed from storage when the event
    is permanently deleted from the database.
    """
    # Delete banner_image if it exists
    if instance.banner_image:
        if default_storage.exists(instance.banner_image.name):
            default_storage.delete(instance.banner_image.name)

    # Delete thumbnail_image if it exists
    if instance.thumbnail_image:
        if default_storage.exists(instance.thumbnail_image.name):
            default_storage.delete(instance.thumbnail_image.name)
