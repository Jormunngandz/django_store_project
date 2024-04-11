import datetime
import decimal
from _decimal import Decimal

from django.db import models
from django.utils.timezone import now, timedelta


def get_date_to() -> datetime.datetime:
    return now() + timedelta(days=7)


class CategoryImage(models.Model):
    src = models.ImageField(
        upload_to="app_category/category/",
        default="app_users/avatars/default.png",
        verbose_name="Ссылка",
    )
    alt = models.CharField(
        max_length=128, verbose_name="Описание", default="Category image"
    )

    def __str__(self):
        return self.alt


class Tag(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self) -> str:
        return self.name


class Sale(models.Model):
    name = models.CharField(max_length=40, default="Sale_name")
    salePrice = models.DecimalField(
        decimal_places=2, max_digits=10, verbose_name="Size of a sale (in %)"
    )
    dateFrom = models.DateTimeField(default=now)
    dateTo = models.DateTimeField(default=get_date_to)

    def __str__(self) -> str:
        return f"{self.name}"


class Category(models.Model):
    title = models.CharField(max_length=40, null=False, blank=False)
    image = models.OneToOneField(
        CategoryImage, on_delete=models.DO_NOTHING, related_name="category"
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="subcategories",
        null=True,
        blank=True,
    )
    tags = models.ManyToManyField(Tag, related_name="category")

    def __str__(self) -> str:
        return self.title


class Product(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.DO_NOTHING, related_name="product", null=True
    )
    price = models.DecimalField(decimal_places=2, max_digits=10)
    count = models.IntegerField(default=0)
    date = models.DateTimeField(default=now)
    title = models.CharField(max_length=50, unique=True)
    description = models.TextField(max_length=500, blank=True, null=True)
    freeDelivery = models.BooleanField(default=False)
    rating = models.DecimalField(decimal_places=1, max_digits=3, default=5)
    limited = models.BooleanField(default=False)
    sale = models.ForeignKey(
        Sale, on_delete=models.SET_NULL, related_name="product", null=True, blank=True
    )

    def return_origin_price(self) -> None:
        if self.sale:
            self.price = Decimal(self.price / (1 - self.sale.salePrice/100)).quantize(
                                    Decimal("0.01"), decimal.ROUND_HALF_UP)

    def make_sale_price(self) -> None:
        self.price = Decimal(self.price * (100 - self.sale.salePrice) / 100).quantize(
            Decimal("0.01"), decimal.ROUND_HALF_UP)

    def __str__(self) -> str:
        # return self.title + " " + self.category
        return f"{self.title} ({self.category})"


class Specification(models.Model):
    name = models.CharField(max_length=40, null=False, blank=False)
    value = models.CharField(max_length=150, null=True, blank=True)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="specifications"
    )


class Review(models.Model):
    author = models.CharField(max_length=30, null=True, blank=False)
    is_checked = models.BooleanField(default=False)
    email = models.EmailField(max_length=30, null=False, blank=False)
    rate = models.IntegerField()
    date = models.DateTimeField(default=now)
    text = models.TextField(max_length=400, null=False, blank=False)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="review"
    )

    def __str__(self) -> str:
        return "review about" + self.product.title


class ProductImage(models.Model):
    src = models.ImageField(
        upload_to="app_products/",
        default="app_users/avatars/default.png",
        verbose_name="Ссылка",
    )
    alt = models.CharField(
        max_length=128, verbose_name="Описание", default="Image alt string"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )

    def __str__(self) -> str:
        return self.alt
