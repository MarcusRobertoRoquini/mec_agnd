from django import template

register = template.Library()

@register.filter
def dict_get(d, key):
    return d.get(key, [])

@register.filter
def split(value, sep=","):
    return value.split(sep)