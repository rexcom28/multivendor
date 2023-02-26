
from django import template
from django.db.models import Count

from store.models import Category
register = template.Library()

@register.inclusion_tag('core/menu.html')
def menu(*args, **kwargs):
    categories = Category.objects.annotate(product_count=Count('products')).filter(product_count__gt=0)
    return {'categories': categories}


@register.simple_tag
def back_button(request):
    
    if request.method == 'GET':
        return True #request.META.get('HTTP_REFERER', '/')
    return False