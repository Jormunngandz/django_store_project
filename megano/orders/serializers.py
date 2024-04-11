from typing import Dict, List

from rest_framework import serializers as s
from .models import Order, OrderItem
from products.serializers import ProductSerializer
from users.serializers import ProfileSerializer


class OrderItemSerialize(s.ModelSerializer):
    product = s.SerializerMethodField()

    def get_product(self, obj: OrderItem) -> Dict:
        data = ProductSerializer(obj.product).data
        data["count"] = obj.count
        return data

    class Meta:
        model = OrderItem
        fields = ["product"]


class OrderSerializer(s.ModelSerializer):
    products = s.SerializerMethodField()
    orderId = s.SerializerMethodField()
    profile = ProfileSerializer()
    createdAt = s.SerializerMethodField()

    def get_products(self, obj: Order) -> List[Dict]:
        order_items = OrderItem.objects.filter(order=obj).all()
        data = []
        for item in order_items:
            serialized_item = (ProductSerializer(item.product)).data
            serialized_item["count"] = item.count
            data.append(serialized_item)
        return data

    def get_createdAt(self, obj: Order) -> str:
        return obj.createdAt.strftime("%Y-%m-%d%H:%M:%S")

    def get_totalCost(self, obj: Order) -> float:
        items = OrderItem.objects.filter(order=obj).all()
        total_price = 0
        for el in items:
            total_price += el.product.price * el.count
        return float(total_price)

    def get_orderId(self, obj: Order) -> int:
        return obj.id

    class Meta:
        model = Order
        fields = [
            "id",
            "products",
            "createdAt",
            "deliveryType",
            "paymentType",
            "status",
            "city",
            "address",
            "totalCost",
            "orderId",
            "profile",
        ]
