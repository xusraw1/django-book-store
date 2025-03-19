# catalog/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Умножает два числа"""
    try:
        return value * arg
    except (TypeError, ValueError):
        return 0
