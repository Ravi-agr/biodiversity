__author__ = 'sawal_000'

from django import template

register = template.Library()
@register.filter
def image(obj, resolution):
    return obj.getURL(resolution)

@register.filter
def common_name(obj):
    cn = obj.getCommonName()
    if cn:
        if "," in cn[0].common_name:
            return cn[0].common_name.split(",")[0]
        return cn[0].common_name
    else:
        return None

@register.filter
def abstract(obj):
    return obj.getAbstract()

@register.filter
def initials(obj):
    arr = obj.split()
    str = ""
    for item in arr:
        str += item[0]
    return str