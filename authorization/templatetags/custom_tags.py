from django import template

register = template.Library()


@register.filter(name='get_range')
def get_range(number):
    return range(number)


@register.simple_tag(takes_context=True)
def query_transform(context, **kwargs):
    query = context['request'].GET.copy()
    for k, v in kwargs.items():
        query[k] = v
    return query.urlencode()
