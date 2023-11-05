from django import template
from django.template import Library

from django.template.defaulttags import register

@register.filter # https://stackoverflow.com/questions/8000022/django-template-how-to-look-up-a-dictionary-value-with-a-variable
def get_item(dictionary, key):
    return dictionary.get(key)