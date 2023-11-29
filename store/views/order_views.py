from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.http.response import JsonResponse
from django.contrib import messages
import json

from ..models import Product


def update_color_size_drop(request):
    user = request.user
    if user.is_authenticated and (user.is_staff or user.is_superuser):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            messages.warning(request, _('Oops! Something went wrong with your request. Please try again.'
                                        ' If the issue persists, contact our support team for assistance.'))
            return JsonResponse('Something went wrong', safe=False)

        product_pk = data.get('productId')

        if product_pk:
            try:
                color_size_query = Product.active_objs.get(pk=product_pk).color_size_values.filter(
                    Q(inventory__gt=0) | Q(inventory=None), is_active=True, )
                data_response = {}
                for value in color_size_query:
                    data_response[str(value)] = value.pk

                return JsonResponse(data_response, safe=False)
            except Product.DoesNotExist:
                messages.error(request, _('Please enter a active product'))
                return JsonResponse('inactive product', safe=False)

        messages.error(request, _('Please enter a product'))
        return JsonResponse('Invalid pk', safe=False)
