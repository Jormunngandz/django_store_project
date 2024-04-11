from typing import List

from django.contrib import admin
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.urls import path
from .forms import AddProductsToSaleForm, AddProduct
from .models import (
    Category,
    CategoryImage,
    Product,
    Tag,
    ProductImage,
    Review,
    Sale,
    Specification,
)


class ProductImageInLine(admin.TabularInline):
    model = ProductImage


class ProductInline(admin.StackedInline):
    model = Product


class SpecificationInLine(admin.StackedInline):
    model = Specification


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = "title", "image"


@admin.register(CategoryImage)
class CategoryImageAdmin(admin.ModelAdmin):
    list_display = "src", "alt"


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    change_list_template = "api/sales_changelist.html"
    change_form_template = "api/sales_change_form.html"
    add_form_template = "api/sales_add_form.html"
    list_display = (
        "name",
        "salePrice",
        "dateFrom",
        "dateTo",
    )

    def change_view(self, request: WSGIRequest,
                    object_id: int,
                    form_url: str = "",
                    extra_context=None) -> TemplateResponse:
        extra_context = extra_context or {}
        form_c = AddProduct(sale=object_id)
        extra_context["form_c"] = form_c
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context
        )

    def add_view(self, request: WSGIRequest, form_url: str = "", extra_context=None) -> TemplateResponse:
        extra_context = extra_context or {}
        extra_context["custom_button"] = True
        form_c = AddProduct()
        extra_context["form_c"] = form_c
        return super().add_view(request, form_url, extra_context=extra_context)

    def get_urls(self) -> List[path]:
        urls = super().get_urls()
        new_urls = [
            path("add_product", self.add_products_to_sale, name="add_products_to_sale")
        ]

        return new_urls + urls

    def response_change(self, request: WSGIRequest, obj: Sale):
        for el in request.POST.getlist("add product"):
            product = Product.objects.filter(id=el).first()
            if product:
                product.sale = obj
                Product.make_sale_price(product)
                product.save()
        for el in request.POST.getlist("delete product"):

            product = Product.objects.get(id=el)
            Product.return_origin_price(product)
            product.sale = None
            product.save()

        return super().response_change(request, obj)

    def response_add(self, request: WSGIRequest, obj: Sale, post_url_continue=None) -> HttpResponse:  # Here

        for el in request.POST.getlist("add product"):
            product = Product.objects.filter(id=el).first()
            if product:
                product.sale = obj
                product.save()
        return super().response_add(request, obj, post_url_continue)

    def add_products_to_sale(self, request: WSGIRequest) -> HttpResponse:
        if request.method == "GET":
            form = AddProductsToSaleForm()
        else:
            form = AddProductsToSaleForm(request.POST)
            if form.is_valid():
                products = Product.objects.filter(id__in=form.data.getlist("products"))
                sale = Sale.objects.get(id=int(form.data["sales"]))
                for product in products:
                    product.sale = sale
                    product.save()
                return HttpResponseRedirect("/admin/products/sale/")
            else:
                raise ValueError
        context = {"form": form}
        return render(request, "admin/add_product_to_sale.html", context)


@admin.action(description="Delete sale from selected products")
def delete_sale(ProductAdmin, request, queryset):
    for el in queryset:
        el.sale = None
        el.save()


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInLine, SpecificationInLine]
    actions = [delete_sale]

    list_display = (
        "title",
        "category",
        "price",
        "count",
        "description",
        "freeDelivery",
        "limited",
        "sale",
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = "src", "alt"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = "author", "email", "rate", "date", "text", "product", "is_checked"
