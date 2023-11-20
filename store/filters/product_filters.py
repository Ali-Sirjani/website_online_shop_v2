from django.db.models import F, Case, When, IntegerField
from django.utils.translation import gettext_lazy as _
import django_filters
from django_filters import widgets
from persiantools.jdatetime import JalaliDateTime

from ..models import Product


def datetime_to_dict_func(dt_obj):
    return {
        'year': dt_obj.year,
        'month': dt_obj.month,
        'day': dt_obj.day,
        'hour': dt_obj.hour,
        'minute': dt_obj.minute,
        'second': dt_obj.second,
        'microsecond': dt_obj.microsecond
    }


def validate_datetime_updated(value):
    if value.start:
        datetime_dict_start = datetime_to_dict_func(value.start)
        value_start = JalaliDateTime(**datetime_dict_start).to_gregorian()
    else:
        value_start = None

    if value.stop:
        datetime_dict_stop = datetime_to_dict_func(value.stop)
        value_stop = JalaliDateTime(**datetime_dict_stop).to_gregorian()
    else:
        value_stop = None

    return slice(value_start, value_stop, None)


class ProductFilter(django_filters.FilterSet):
    price = django_filters.NumericRangeFilter(method='custom_filter_price')
    datetime_updated = django_filters.DateFromToRangeFilter(label=_('date'), widget=widgets.DateRangeWidget(
        attrs={'class': 'jalali_date-date'}), method='custom_filter_datetime')

    class Meta:
        model = Product
        fields = ('price', 'datetime_updated', 'discount')

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

    def custom_filter_datetime(self, queryset, name, value):
        value_validate = validate_datetime_updated(value)

        start_value, stop_value = value_validate.start, value_validate.stop

        if start_value and stop_value:
            queryset = queryset.filter(datetime_updated__gte=start_value, datetime_updated__lte=stop_value)

        elif start_value:
            queryset = queryset.filter(datetime_updated__gte=start_value)

        elif stop_value:
            queryset = queryset.filter(datetime_updated__lte=stop_value)

        return queryset
