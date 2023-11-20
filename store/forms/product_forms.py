from django import forms
from django.utils.translation import gettext_lazy as _

from ..models import Product, ProductColorAndSizeValue, ProductImage, ProductComment


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

        elif discount and discount_price is None:
            self.add_error('discount_price', _('You must fill out discounts price because you active discount'))

        elif discount_price is not None and price <= discount_price:
            self.add_error('discount_price', _('The value of discount price must be less than from price'))

        return clean_data


class InventoryForm(forms.Form):
    inventory = forms.IntegerField(widget=forms.NumberInput(attrs={'min': 0}))


class ProductColorAndSizeValueFormAdmin(forms.ModelForm):
    class Meta:
        model = ProductColorAndSizeValue
        fields = ('color', 'size', 'size_price', 'inventory',)

    def clean(self):
        """
        Custom clean method for ProductColorAndSizeValueFormAdmin.
        Adjusts the product inventory by subtracting the form's 'inventory' value.
        Validates that the sum of 'inventory' values across colors is equal to the total 'inventory' of the product.

        Returns:
        - clean_data: The cleaned form data.
        """

        # Calling the clean method of the superclass to ensure basic validation
        clean_data = super().clean()

        # Extracting 'product' and 'inventory' from the cleaned data
        product = clean_data.get('product')
        inventory = clean_data.get('inventory')

        # Checking if 'product' and 'inventory' are present
        if product and inventory:
            # Adjusting the product inventory based on the current form's inventory value
            self.product_inventory[0] -= inventory

            # Validating that the sum of color inventories is equal to the product inventory
            if self.product_inventory[0] < 0:
                self.add_error(None, 'Sum inventory of colors must be equal to product inventory')

        return clean_data


class ProductImageValueFormAdmin(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ('image', 'is_main',)

    def clean(self):
        clean_data = super().clean()
        is_main = clean_data.get('is_main')

        if is_main:
            if self.is_main_set[0]:
                self.add_error('is_main', 'One image can be main image')
            else:
                self.is_main_set[0] = True

        return clean_data


class SearchForm(forms.Form):
    q = forms.CharField()


class ProductCommentForm(forms.ModelForm):
    class Meta:
        model = ProductComment
        fields = ('text', 'star')

