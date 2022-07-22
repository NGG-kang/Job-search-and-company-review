# app/templatetags/util.py
from django import template

register = template.Library()

@register.filter
def get_type(value):
    return type(value).__name__


@register.filter
def percentage(value):
    if value:
        return str(round((float(value) * 100), 0)) + "%"
    return "None"


@register.filter
def is_bool(value):
    if value == "true":
        return True
    return False