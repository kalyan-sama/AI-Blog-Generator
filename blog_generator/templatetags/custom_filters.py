from django import template
import re

register = template.Library()

@register.filter
def replace_double_asterisks(value):
    return re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', value)
