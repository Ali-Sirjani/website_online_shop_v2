from django import forms
from django.utils.translation import gettext_lazy as _
from django.forms.models import BaseInlineFormSet

from ..models import Product, ProductComment


class ProductFormAdmin(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('title', 'description', 'short_description', 'category', 'price',
                  'discount', 'discount_price', 'discount_timer', 'inventory', 'slug_change', 'slug')
        widgets = {
            'short_description': forms.Textarea(attrs={'cols': 75, 'rows': 5})
        }

    def clean(self):
        clean_data = super().clean()
        price = clean_data.get('price')
        discount = clean_data.get('discount')
        discount_price = clean_data.get('discount_price')
        inventory = clean_data.get('inventory')
        is_active = clean_data.get('is_active')

        if not discount and discount_price:
            self.add_error('discount', _('You must set discount because you fill out discount price'))

        elif discount and discount_price is None:
            self.add_error('discount_price', _('You must fill out discounts price because you active discount'))

        elif discount_price is not None and price <= discount_price:
            self.add_error('discount_price', _('The value of discount price must be less than from price'))

        if (inventory is not None) and (inventory <= 0) and is_active:
            self.add_error('inventory', _('Products with 0 or negative inventory cannot be activated'))

        return clean_data


class InventoryForm(forms.Form):
    inventory = forms.IntegerField(widget=forms.NumberInput(attrs={'min': 0}))


class ProductColorAndSizeValueFormSetAdmin(BaseInlineFormSet):
    def clean(self):
        if self.product_inventory > 0:
            sum_inventory = 0

            for form in self.forms:
                inventory = form.cleaned_data.get('inventory')
                size = form.cleaned_data.get('size')
                color = form.cleaned_data.get('color')
                if not (size or color):
                    form.add_error(None, 'Please provide either the size or the color for the product.')

                if inventory:
                    sum_inventory += inventory

            if self.product_inventory - sum_inventory < 0:
                raise forms.ValidationError('Sum inventory of colors must be equal to product inventory')

        return super().clean()


class ProductImageTabuFormSetAdmin(BaseInlineFormSet):
    def clean(self):
        main_count = 0

        for form in self.forms:
            if form.cleaned_data.get('is_main'):
                main_count += 1

        if main_count != 1:
            raise forms.ValidationError('Exactly one image should be marked as main.')

        return super().clean()


class SearchForm(forms.Form):
    q = forms.CharField()


class ProductCommentForm(forms.ModelForm):
    class Meta:
        model = ProductComment
        fields = ('text', 'star')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        text_field = self.fields.get('text')
        if text_field:
            text_field.widget.attrs['class'] = ''
