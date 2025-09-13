import os
from datetime import date

from django.core.files.storage import default_storage
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from .models import AdManager, AdPlacement, normalize_positions


def safe_delete_file(file_path):
    """
    Safely delete a file from storage, handling exceptions gracefully.

    Args:
        file_path (str): The path to the file to delete

    Returns:
        bool: True if file was deleted successfully or didn't exist, False if error occurred
    """
    if not file_path:
        return True

    try:
        if default_storage.exists(file_path):
            default_storage.delete(file_path)
            print(f"✅ Deleted file: {file_path}")
            return True
        else:
            print(f"ℹ️  File doesn't exist: {file_path}")
            return True
    except Exception as e:
        print(f"❌ Error deleting file {file_path}: {str(e)}")
        return False


@receiver(pre_save, sender=AdManager)
def ad_manager_pre_save(sender, instance, **kwargs):
    """Handle pre-save operations for AdManager instances."""
    # Set duration if start and end dates are provided
    if instance.start_datetime and instance.end_datetime:
        instance.active_ad_period = instance.end_datetime - instance.start_datetime

    # Auto-deactivate if overdue exceeds limit
    if instance.end_datetime and instance.limited_overdue is not None:
        actual_overdue = (date.today() - instance.end_datetime).days
        if actual_overdue > instance.limited_overdue:
            instance.is_active = False

    # Handle poster file cleanup when image is changed
    if instance.pk:  # Only for existing instances (updates)
        try:
            # Get the old instance to compare poster fields
            old_instance = AdManager.objects.get(pk=instance.pk)

            # If poster has changed and old poster exists, delete the old file
            if old_instance.poster and old_instance.poster != instance.poster:
                if old_instance.poster.name != (instance.poster.name if instance.poster else None):
                    safe_delete_file(old_instance.poster.name)
                    print(
                        f"🔄 Replaced poster for ad '{instance.campaign_title}': {old_instance.poster.name} → {instance.poster.name if instance.poster else 'None'}")

        except AdManager.DoesNotExist:
            # Instance doesn't exist yet, this is a new creation
            pass
        except Exception as e:
            print(f"⚠️  Error checking for old poster file: {str(e)}")


@receiver(post_delete, sender=AdManager)
def ad_manager_post_delete(sender, instance, **kwargs):
    """Handle cleanup when AdManager instance is deleted."""
    # Delete associated poster file when ad is deleted
    if instance.poster:
        safe_delete_file(instance.poster.name)
        print(
            f"🗑️  Deleted poster for removed ad '{instance.campaign_title}': {instance.poster.name}")


@receiver([post_save, post_delete], sender=AdPlacement)
def auto_normalize_positions(sender, instance, **kwargs):
    normalize_positions(instance.ad_space)
