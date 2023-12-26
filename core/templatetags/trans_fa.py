from django.template import library
from django.utils.safestring import mark_safe

register = library.Library()


@register.filter
def num_fa_15(value):
    persian = '۰١٢٣۴۵٦٧٨٩'
    engilish = '0123456789'
    try:
        value = str(f'{value:,}')
    except ValueError:
        pass

    trans_table = str.maketrans(engilish, persian)
    translated_value = value.translate(trans_table)

    translated_value = f'<strong style="font-size: 15px;" dir="ltr">{translated_value}</strong>'

    return mark_safe(translated_value)


@register.filter
def num_fa_20(value):
    persian = '۰١٢٣۴۵٦٧٨٩'
    engilish = '0123456789'
    try:
        value = str(f'{value:,}')
    except ValueError:
        pass

    trans_table = str.maketrans(engilish, persian)
    translated_value = value.translate(trans_table)

    translated_value = f'<strong style="font-size: 20px;" dir="ltr">{translated_value}</strong>'

    return mark_safe(translated_value)


@register.filter
def num_fa_25(value):
    persian = '۰١٢٣۴۵٦٧٨٩'
    engilish = '0123456789'
    try:
        value = str(f'{value:,}')
    except ValueError:
        pass

    trans_table = str.maketrans(engilish, persian)
    translated_value = value.translate(trans_table)

    translated_value = f'<strong style="font-size: 25px;" dir="ltr">{translated_value}</strong>'

    return mark_safe(translated_value)

