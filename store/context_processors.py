from django.utils.translation import gettext_lazy as _
from django.db.models import Prefetch

from .models import Category, Order, OrderItem
from .cart import Cart


def product_contexts(request):
    sort_dict = {_('Cheapest'): 1, _('Most Expensive'): 2, _('Newest'): 3, _('Oldest'): 4}
    context = {
        'categories': Category.objects.all(),
        'sort_dict': sort_dict,
    }
    return context


def order_contexts(request):
    if request.user.is_authenticated:
        order, created = Order.objects.prefetch_related(
            Prefetch(
                'items',
                queryset=OrderItem.objects.select_related('product').all()
            )).get_or_create(customer=request.user, completed=False)
    else:
        order = Cart(request)

    context = {
        'order': order,
    }

    return context
