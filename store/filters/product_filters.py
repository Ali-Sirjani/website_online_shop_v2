from django.db.models import F, Case, When, IntegerField
import django_filters

from ..models import Product


class ProductFilter(django_filters.FilterSet):
    price = django_filters.NumericRangeFilter(method='custom_filter_price')

    class Meta:
        model = Product
        fields = ('price', 'discount',)

    def custom_filter_price(self, queryset, name, value):
        start_value, stop_value = value.start, value.stop
        queryset_based_price = queryset.annotate(
            effective_price=Case(
                When(discount=True, then=F('discount_price')),
                default=F('price'),
                output_field=IntegerField()
            )
        )
        if start_value and stop_value:
            queryset_based_price = queryset_based_price.filter(effective_price__gte=start_value,
                                                               effective_price__lte=stop_value)

        elif start_value:
            queryset_based_price = queryset_based_price.filter(effective_price__gte=start_value)

        elif stop_value:
            queryset_based_price = queryset_based_price.filter(effective_price__lte=stop_value)

        return queryset_based_price
