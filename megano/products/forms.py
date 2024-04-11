from django import forms
from django.db.models import Q

from .models import Sale, Product


class AddProductsToSaleForm(forms.Form):
    sale_choices = [(sale.id, sale.name) for sale in Sale.objects.all()]
    product_choices = [(product.title, product.id) for product in Product.objects.all().order_by("category")]

    sales = forms.ChoiceField(choices=sale_choices)
    products = forms.ModelMultipleChoiceField(queryset=Product.objects.all().order_by("category"))


class AddProduct(forms.Form):
    def __init__(self, sale=None, **kwargs):
        self.sale = sale
        super().__init__(**kwargs)
        if sale:
            self.fields['delete product'] = \
                forms.ModelMultipleChoiceField(queryset=Product.objects.filter(sale=sale).all().order_by("category"))
            self.fields['add product'] = \
                forms.ModelMultipleChoiceField(queryset=Product.objects.filter(~Q(sale=sale)).all().order_by("category"))
        else:
            self.fields['add product'] = \
                forms.ModelMultipleChoiceField(
                    # queryset=Product.objects.filter(sale=None).all().order_by("category"))
                    queryset=Product.objects.all().order_by("category"))
