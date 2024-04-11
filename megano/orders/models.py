from django.db import models

from products.models import Product
from users.models import Profile


class Order(models.Model):
    createdAt = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    profile = models.ForeignKey(
        Profile, null=True, blank=True, on_delete=models.DO_NOTHING
    )
    fullName = models.CharField(
        null=True, blank=True, max_length=100, verbose_name="Полное имя"
    )
    phone = models.PositiveIntegerField(null=True, blank=True, verbose_name="Телефон")
    email = models.EmailField(null=True, blank=True, verbose_name="Email")
    address = models.CharField(
        null=True, blank=True, max_length=100, verbose_name="Адрес"
    )
    city = models.CharField(null=True, blank=True, max_length=100, verbose_name="Город")
    deliveryType = models.CharField(max_length=30, default="paid")
    paymentType = models.CharField(max_length=30, default="online")
    status = models.CharField(max_length=30, default="accepted")
    session_id = models.CharField(max_length=100, null=True, blank=True)
    updated = models.BooleanField(default=True)
    totalCost = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Цена заказа", default=0
    )


class OrderItem(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, null=False, blank=False
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="order_item",
    )
    count = models.IntegerField(default=1)
