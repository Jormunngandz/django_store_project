from django.urls import path

from .views import OrderView, OrderDetailedView, BasketView, PaymentView

urlpatterns = [
    path('orders', OrderView.as_view(), name='orders'),
    path('order/<int:pk>', OrderDetailedView.as_view(), name='order'),
    path('basket', BasketView.as_view(), name='basket'),
    path('payment/<int:pk>', PaymentView.as_view(), name='payment'),
]
