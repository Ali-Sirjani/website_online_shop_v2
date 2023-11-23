from django.utils.translation import gettext_lazy as _

from .models import Category


def product_contexts(request):
    sort_dict = {_('Cheapest'): 1, _('Most Expensive'): 2, _('Newest'): 3, _('Oldest'): 4}
    context = {
        'categories': Category.objects.all(),
        'sort_dict': sort_dict,
    }
    return context
