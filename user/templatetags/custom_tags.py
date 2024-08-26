"""
This is custom tags to create a greeting based on time
"""
from datetime import datetime

from django import template


register = template.Library()


@register.filter
def greeting(time=None):
    """ Greeting based on time """
    if not time:
        time = datetime.now().hour
    else:
        time = int(time)

    if 5 <= time < 12:
        return "morning"
    elif 12 <= time < 18:
        return "afternoon"
    elif 18 <= time < 22:
        return "evening"

    return "night"
