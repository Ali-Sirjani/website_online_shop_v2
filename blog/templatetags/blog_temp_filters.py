from django.template import library

register = library.Library()


@register.filter
def remove_obsolete_pages_blog(data):
    if 'page' in data:
        data._mutable = True
        data.pop('page')
        data._mutable = False
    return data.urlencode()


@register.filter
def remove_obsolete_sorts_blog(data):
    data._mutable = True
    if 'sort' in data:
        data.pop('sort')
    if 'page' in data:
        data.pop('page')
    data._mutable = False
    return data.urlencode()
