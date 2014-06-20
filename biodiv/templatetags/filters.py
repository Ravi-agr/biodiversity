__author__ = 'sawal_000'

from django import template

register = template.Library()
@register.filter
def image(obj, resolution):
    return obj.getURL(resolution)