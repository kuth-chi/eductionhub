from django import template

register = template.Library()

@register.filter
def format_kh_phone(value):
    number = str(value)
    if number.startswith('+855') and len(number) == 12:
        # Format: +855 XX XXX XXXX
        return f"{number[:4]} {number[4:6]} {number[6:9]} {number[9:]}"
    return number 
