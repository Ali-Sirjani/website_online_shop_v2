from django.db.models import F, Case, When, IntegerField, Prefetch

from ..models import ProductColorAndSizeValue, ProductSpecificationValue


def sort_product_queryset(sort_num, queryset):
    if sort_num in ['1', '2', '3', '4']:
        if sort_num == '1':
            sort_by = 'price'
        elif sort_num == '2':
            sort_by = '-price'
        elif sort_num == '3':
            sort_by = '-datetime_created'
        else:
            sort_by = 'datetime_created'

        if 'price' in sort_by:
            queryset = queryset.annotate(
                effective_price=Case(
                    When(discount=True, then=F('discount_price')),
                    default=F('price'),
                    output_field=IntegerField()
                )
            )

            if sort_by == 'price':
                queryset = queryset.order_by('effective_price')

            elif sort_by == '-price':
                queryset = queryset.order_by('-effective_price')

        else:
            queryset = queryset.order_by(sort_by)

    return queryset


def optimize_product_query(queryset):
    """
    Prefetching related data to optimize database queries
    - 'specs_values': Prefetching 'ProductSpecificationValue' objects with their related 'specification' objects
    - 'color_size_values': Prefetching 'ProductColorAndSizeValue' objects with their related 'color' and 'size' objects
    - 'images': Prefetching related 'Image' objects
    """
    queryset = queryset.prefetch_related(
        Prefetch(
            'specs_values',
            queryset=ProductSpecificationValue.objects.select_related('specification')
        ),
        Prefetch(
            'color_size_values',
            queryset=ProductColorAndSizeValue.objects.select_related('color', 'size')
        ),
        'images',
    )

    return queryset
