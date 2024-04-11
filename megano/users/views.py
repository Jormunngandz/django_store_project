from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework import permissions
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import JSONParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from upload_validator import FileTypeValidator

from .models import Profile, Avatar
from .serializers import ProfileSerializer
from orders.cart import Basket
from orders.models import Order, OrderItem


class RegisterView(APIView):
    def post(self, request: Request) -> Response:
        data = JSONParser().parse(request)
        try:
            user = User.objects.create_user(
                username=data["username"], password=data["password"]
            )
            Profile.objects.create(user=user, fullName=data["name"])
            auth_user = authenticate(
                request, username=data["username"], password=data["password"]
            )
            if auth_user is not None:
                login(request, auth_user)

                return Response(status=200)
            return Response(status=500)
        except Exception:
            return Response(status=500)

    def get(self, request: Request):
        return Response(status=200)


class LogOutView(APIView):
    def post(self, request: Request) -> Response:
        logout(request)
        return Response(status=200)


class LogInView(APIView):
    def post(self, request: Request) -> Response:
        data = JSONParser().parse(request)
        user = authenticate(username=data["username"], password=data["password"])
        if user is not None:
            """После аутентификации проверяем наличие товаров в корзине на момент до авторизации, далее авторизуем
            пользователя, проверяем есть ли у пользователя недооформленый заказ, если в корзине присутствовали товары 
            до момента авторизации и после был неоформленный заказ, то добавляем товары из корзины к заказу, а товары 
            из заказа помещаем в корзину.
            Если же недооформленого заказа не было - удаляем заказ созданный без авторизации.
            Если же заказа не было, но в корзине были товары на момент авторизации то добавляем их в корзину
            авторизированного пользователя
            """
            order_by_anon = Order.objects.filter(
                paid=False, session_id=request.session.session_key
            ).first()
            login(request=request, user=user)
            unfinished_order = Order.objects.filter(
                paid=False, profile__user=user
            ).first()
            basket = Basket(request)
            if unfinished_order and order_by_anon:
                order_by_anon.profile = Profile.objects.get(user=user)
                unfinished_order_items = OrderItem.objects.filter(
                    order=unfinished_order
                )

                for un_order_item in unfinished_order_items:
                    item_in_anon_order_exist = order_by_anon.order_item.filter(
                        product=un_order_item.product
                    ).first()
                    if item_in_anon_order_exist:
                        item_in_anon_order_exist.count += un_order_item.count
                        item_in_anon_order_exist.save()
                    else:
                        item_in_anon_order_exist = OrderItem.objects.create(
                            order=order_by_anon,
                            product=un_order_item.product,
                            count=un_order_item.count,
                        )
                    order_by_anon.totalCost += (
                        item_in_anon_order_exist.product.price * un_order_item.count
                    )
                    basket.add(
                        un_order_item.product,
                        quantity=un_order_item.count,
                    )

                order_by_anon.save()
                unfinished_order.delete()
            elif order_by_anon:
                order_by_anon.delete()
            elif unfinished_order:
                list(
                    map(
                        lambda add_item: basket.add(
                            add_item.product, quantity=add_item.count
                        ),
                        OrderItem.objects.filter(order=unfinished_order),
                    )
                )
            return Response(status=200)
        else:
            return Response(status=500)


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        profile = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        profile = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)


class ProfileAvatarView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:
        avatar_upload_path = "api/uploads/app_users/avatars/user_avatars"
        in_memory_img: InMemoryUploadedFile = request.FILES["avatar"]
        validator = FileTypeValidator(allowed_types=["image/jpeg", "image/png"])
        try:
            validator(in_memory_img)
            avatar = Profile.objects.get(user_id=request.user.id).avatar
            if avatar:
                FileSystemStorage(avatar_upload_path).delete(
                    name=avatar.src.name[avatar.src.name.rfind("/") + 1 :]
                )
                avatar.src.save(in_memory_img.name, in_memory_img)
            else:
                new_avatar = Avatar.objects.create(
                    alt=in_memory_img.name, src=in_memory_img
                )
                profile = Profile.objects.get(user=self.request.user)
                profile.avatar = new_avatar
                profile.save()
            return Response(status=200)
        except ValidationError:
            return Response(status=400)


class ProfilePassportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:
        user = User.objects.get(id=request.user.id)
        if authenticate(username=user, password=request.data["currentPassword"]):
            user.set_password(request.data["newPassword"])
            user.save()
            return Response(status=200)
        return Response(status=400)
