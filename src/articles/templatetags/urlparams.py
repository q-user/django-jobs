from django import template

register = template.Library()


@register.simple_tag
def add_query_params(request, **kwargs):
    updated = request.GET.copy()
    for k, v in kwargs.items():
        updated[k] = v
    return request.build_absolute_uri('?' + updated.urlencode())
