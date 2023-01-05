from django import template

register = template.Library()

@register.filter
def to_line(value):
    return value.replace('/', ' --- ')