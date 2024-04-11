from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from products.serializers import ProductSerializer
from users.models import Profile

from .models import Order, OrderItem
from .cart import Basket
from products.models import Product

from .serializers import OrderSerializer
from users.serializers import ProfileSerializer


class OrderView(APIView):
    def post(self, request: Request) -> Response:
        if request.user.is_authenticated:
            profile = Profile.objects.filter(user=request.user).first()
            order = Order.objects.filter(profile=profile, paid=False).first()
            if not order:
                order = Order.objects.create(profile=profile)
                order.profile = profile
        else:
            order = Order.objects.filter(
                session_id=request.session.session_key, paid=False
            ).first()
            if not order:
                order = Order.objects.create(session_id=request.session.session_key)

        if order.updated:
            basket = Basket(request)
            OrderItem.objects.filter(order=order).all().delete()
            products = Product.objects.filter(id__in=basket.basket.keys()).all()
            if products:
                order.totalCost = sum(
                    (
                        el.product.price * el.count if not el.product.sale else
                        el.product.price
                        for el in [
                            OrderItem.objects.create(
                                order=order,
                                product=product,
                                count=basket.basket.get(str(product.id))["count"],
                            )
                            for product in products
                        ]
                    )
                )
            order.updated = False
        order.save()
        return Response(data=OrderSerializer(order).data, status=200)

    def get(self, request: Request) -> Response:
        orders = Order.objects.filter(profile__user_id=request.user.id).all()
        if orders:
            return Response(data=OrderSerializer(orders, many=True).data, status=200)
        return Response(status=404)


class OrderDetailedView(APIView):
    def post(self, request: Request, pk: int) -> Response:
        order = Order.objects.filter(id=pk).first()
        if not order:
            return Response(status=404)
        order.paymentType = request.data["paymentType"]
        order.fullName = request.data["fullName"]
        order.phone = request.data["phone"]
        order.email = request.data["email"]
        order.deliveryType = request.data["deliveryType"]
        order.city = request.data["city"]
        order.address = request.data["address"]
        order.save()
        return Response(data=OrderSerializer(order).data, status=200)

    def get(self, request: Request, pk: int) -> Response:
        order = Order.objects.filter(pk=pk).first()

        if not order:
            return Response(status=404)
        data = OrderSerializer(order).data
        data.update(**ProfileSerializer(order.profile).data)
        return Response(data=data, status=200)


class BasketView(APIView):
    def set_update_order_status(self, request: Request) -> None:
        if request.user.is_authenticated:
            order = Order.objects.filter(profile__user=request.user, paid=False).first()
        else:
            order = Order.objects.filter(
                session_id=request.session.session_key, paid=False
            ).first()
        if order:
            order.updated = True
            order.save()

    def get(self, request: Request) -> Response:
        basket = Basket(request)
        return Response(basket.basket.values(), status=200)

    def post(self, request: Request) -> Response:
        product_id = request.data.get("id")
        quantity = int(request.data.get("count", 1))
        product = Product.objects.filter(id=product_id).first()
        if not product:
            return Response(status=404)
        basket = Basket(request)
        basket.add(product, quantity)
        self.set_update_order_status(request)
        return Response(basket.basket.values(), status=200)

    def delete(self, request: Request) -> Response:
        basket = Basket(request)
        count = request.data.get("count", 1)
        basket.remove(request.data.get("id"), count)
        self.set_update_order_status(request)
        return Response(basket.basket.values(), status=200)


class PaymentView(APIView):
    def post(self, request: Request, pk) -> Response:
        basket = Basket(request)
        basket.clear()
        order = Order.objects.filter(pk=pk).first()
        if order:
            order.paid = True
            order.status = "Paid"
            order.save()
            return Response(status=200)
        return Response(status=400)
