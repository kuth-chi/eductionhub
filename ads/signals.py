from datetime import date

from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from .models import AdManager, AdPlacement, normalize_positions


@receiver(pre_save, sender=AdManager)
def ad_manager_pre_save(sender, instance, **kwargs):
    # Set duration if start and end dates are provided
    if instance.start_datetime and instance.end_datetime:
        instance.active_ad_period = instance.end_datetime - instance.start_datetime

    # Auto-deactivate if overdue exceeds limit
    if instance.end_datetime and instance.limited_overdue is not None:
        actual_overdue = (date.today() - instance.end_datetime).days
        if actual_overdue > instance.limited_overdue:
            instance.is_active = False


@receiver([post_save, post_delete], sender=AdPlacement)
def auto_normalize_positions(sender, instance, **kwargs):
    normalize_positions(instance.ad_space)
