# ad_tags.py
from django import template
from ads.models import AdManager
from collections import defaultdict

register = template.Library()

@register.simple_tag
def get_ads_grouped_by_type():
    ads = AdManager.objects.filter(is_active=True).select_related('ad_type')
    if not ads.exists():
        return {}  # Return empty dict to avoid errors

    grouped = defaultdict(list)
    for ad in ads:
        ad_type_name = ad.ad_type.name if ad.ad_type else 'No Type'
        grouped[ad_type_name].append(ad)
    return dict(grouped)
