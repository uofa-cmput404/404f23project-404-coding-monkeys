from django import template
from django.template import Library

register = Library()

@register.simple_tag
def update_variable(value):
    """Allows to update existing variable in template"""
    return value

