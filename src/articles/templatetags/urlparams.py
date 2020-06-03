from django import template

register = template.Library()


@register.simple_tag
def add_query_params(request, **kwargs):
    updated = request.GET.copy()
    for k, v in kwargs.items():
        updated[k] = v
    return request.build_absolute_uri('?' + updated.urlencode())


@register.simple_tag
def remove_query_params(request, *args):
    updated = request.GET.copy()
    for arg in args:
        updated.pop(arg, None)
    return request.build_absolute_uri('?' + updated.urlencode())
