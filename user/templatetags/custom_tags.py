"""
This is custom tags to create a greeting based on time
"""
from datetime import datetime

import pytz
from django import template
from django.utils.timezone import activate, localtime

from user.models import Profile

register = template.Library()


@register.filter
def greeting(user):
    """ Greeting based on user's local time """
    user_profile = Profile.objects.get(user=user)
    user_timezone = pytz.timezone(user_profile.timezone)

    # Activate user's time zone
    activate(user_timezone)

    # Get the current time in the user's time zone
    user_local_time = localtime().hour

    if 5 <= user_local_time < 12:
        return "morning"
    elif 12 <= user_local_time < 18:
        return "afternoon"
    elif 18 <= user_local_time < 22:
        return "evening"

    return "night"