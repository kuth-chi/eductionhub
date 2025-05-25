
from django import template
from ads.models import AdPlacement

register = template.Library()

@register.simple_tag
def get_home_ads():
    return (
        AdPlacement.objects
        .select_related("ad", "ad_space")
        .filter(ad_space__slug = "homepage_banner", ad__is_active=True)
        .order_by('position')
    )