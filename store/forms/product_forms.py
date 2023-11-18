from django import forms
from django.utils.translation import gettext_lazy as _

from ..models import Product, ProductColorValue


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

        if not discount and discount_price:
            self.add_error('discount', _('You must set discount because you fill out discount price'))

        elif discount_price is None:
            self.add_error('discount_price', _('You must fill out discounts price because you active discount'))

        elif price <= discount_price:
            self.add_error('discount_price', _('The value of discount price must be less than from price'))

        return clean_data


class InventoryForm(forms.Form):
    inventory = forms.IntegerField(widget=forms.NumberInput(attrs={'min': 0}))


class ProductColorValueFormAdmin(forms.ModelForm):
    class Meta:
        model = ProductColorValue
        fields = ('color', 'inventory')

    def clean(self):
        clean_data = super().clean()
        product = clean_data.get('product')
        inventory = clean_data.get('inventory')

        if product and inventory:
            product.inventory -= inventory
            if product.inventory < 0:
                request_inventory = self.request_inventory
                inventory_form = InventoryForm(data={'inventory': request_inventory})
                if inventory_form.is_valid():
                    product.inventory = inventory_form.cleaned_data.get('inventory')
                    product.save()

                self.add_error(None, 'Sum inventory of colors must be equal to product inventory')

            else:
                product.save()

        return clean_data
