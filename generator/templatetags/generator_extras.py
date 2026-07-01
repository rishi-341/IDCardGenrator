from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Access a dict value by key in templates."""
    if isinstance(dictionary, dict):
        return dictionary.get(key, '')
    return ''
