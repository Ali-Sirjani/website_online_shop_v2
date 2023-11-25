import copy

from django import forms
from django.utils.translation import gettext_lazy as _

from ..models import Coupon, Order, OrderItem, ShippingAddress


class CouponAdminForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ('code', 'start_date', 'end_date', 'num_available', 'num_used', 'reason_make', 'is_active')

    def clean(self):
        clean_data = super().clean()
        start_date = clean_data.get('start_date')
        end_date = clean_data.get('end_date')
        num_available = clean_data.get('num_available')
        num_used = clean_data.get('num_used')

        if (start_date and not end_date) or (not start_date and end_date):
            self.add_error(None, _('You must fill out both star date and end date, when you enter one of them!'))

        if (num_available and not num_used) or (not num_available and num_used):
            self.add_error(None, _('You must fill out both num available and num used, when you enter one of them!'))

        return clean_data


class CouponRuleAdminFormSet(forms.BaseInlineFormSet):
    def clean(self):
        forms_copy = copy.deepcopy(self.forms)
        start_price_list = [form.instance.start_price for form in forms_copy]
        start_price_list.sort()

        forms_copy.sort(key=lambda form: form.cleaned_data.get('discount_percentage', 0))

        for form, price in zip(forms_copy, start_price_list):
            if form.cleaned_data.get('start_price') != price:
                raise forms.ValidationError('Bigger discount must have bigger start price')

        return super().clean()
