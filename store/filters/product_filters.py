from django.db.models import F, Case, When, IntegerField, Q
from django.utils.translation import gettext_lazy as _
import django_filters
from django_filters import widgets
from persiantools.jdatetime import JalaliDateTime

from ..models import Product, ProductSize, ProductColor


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

    color = django_filters.ModelChoiceFilter(
        queryset=ProductColor.objects.all(),
        field_name='color_size_values__color',
        to_field_name='name',
        label=_('color'),
        method='custom_filter_color_and_size',
    )
    size = django_filters.ModelChoiceFilter(
        queryset=ProductSize.objects.all(),
        field_name='color_size_values__size',
        to_field_name='size',
        label=_('size'),
        method='custom_filter_color_and_size',
    )
    consider_both = django_filters.BooleanFilter(
        label=_('Consider both color and size'),
        method='custom_filter_color_and_size',
    )

    class Meta:
        model = Product
        fields = ('price', 'datetime_updated', 'discount', 'size', 'color')

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

    def custom_filter_color_and_size(self, queryset, name, value):
        data = self.data
        color_value = data.get('color')
        size_value = data.get('size')
        consider_both_value = data.get('consider_both')
        if color_value and size_value and consider_both_value == 'true':
            queryset = queryset.filter(
                color_size_values__color__name=color_value,
                color_size_values__size__size=size_value
            ).distinct()
        else:
            queryset = queryset.filter(
                Q(color_size_values__color__name=color_value) | Q(color_size_values__size__size=size_value)
            ).distinct()

        return queryset
