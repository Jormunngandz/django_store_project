from rest_framework.request import Request
from django.conf import settings

from products.models import Product
from products.serializers import ProductSerializer


class Basket:
    def __init__(self, request: Request) -> None:
        self.session = request.session
        basket = self.session.get(settings.BASKET_SESSION_ID)
        if not basket:
            basket = self.session[settings.BASKET_SESSION_ID] = {}
        self.basket = basket

    def add(self, product: Product, quantity: int = 1) -> None:
        product_id = str(product.id)
        if product_id not in self.basket:
            self.basket[product_id] = ProductSerializer(product).data
            self.basket[product_id]["count"] = quantity
        else:
            self.basket[product_id]["count"] += quantity
        self.save()

    def save(self) -> None:
        self.session[settings.BASKET_SESSION_ID] = self.basket
        self.session.modified = True

    def remove(self, product: Product, quantity: int) -> None:
        product_id = str(product)
        if product_id in self.basket:
            if quantity >= self.basket[product_id]["count"]:
                del self.basket[product_id]
            else:
                self.basket[product_id]["count"] -= quantity
            self.save()

    def clear(self) -> None:
        del self.session[settings.BASKET_SESSION_ID]
        self.session.modified = True
