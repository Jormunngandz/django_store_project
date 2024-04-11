from _decimal import Decimal
from django.db.models import QuerySet, Count, Q, Avg
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from .models import Category, Product, Tag, Review
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    TagSerializer,
    ReviewSerializer,
    ProductSaleSerializer,
)


class CategoriesView(APIView):
    def get(self, request: Request) -> Response:
        q_data = Category.objects.filter(parent=None)
        serialized = CategorySerializer(q_data, many=True)
        return Response(data=serialized.data, status=200)


class CatalogView(APIView, PageNumberPagination):
    page_size = 3
    page_query_param = "currentPage"
    page_size_query_param = "limit"
    max_page_size = 4

    def get(self, request: Request) -> Response:
        category = request.query_params.get("category")
        if category:
            queryset = Product.objects.filter(
                Q(category_id=category) | Q(category__parent_id=category)
            ).prefetch_related("images")
        else:
            queryset = Product.objects.prefetch_related("images")
        name = request.query_params.get("filter[name]")
        if name:
            queryset = queryset.filter(
                Q(description__icontains=name) | Q(title__icontains=name)
            )

        min_price = Decimal(request.query_params.get("filter[minPrice]", 0))
        max_price = Decimal(request.query_params.get("filter[maxPrice]", 50000))
        queryset = queryset.filter(price__range=(min_price, max_price))

        free_delivery = request.query_params.get("filter[freeDelivery]")
        if free_delivery == "true":
            queryset = queryset.filter(freeDelivery=True)

        available = request.query_params.get("filter[available]")
        if available == "true":
            queryset = queryset.filter(count__gt=0)

        tags = request.query_params.getlist("tags[]")
        if tags:
            req_category = Category.objects.filter(
                Q(tags__in=tags) | Q(parent__tags__in=tags)
            )
            queryset = queryset.filter(category__in=list(req_category))

        sort_field = request.query_params.get("sort")
        sort_type = request.query_params.get("sortType")
        if sort_field == "rating":
            if sort_type == "dec":
                queryset = queryset.order_by("-rating")
            else:
                queryset = queryset.order_by("rating")
        elif sort_field == "reviews":
            if sort_type == "dec":
                queryset = queryset.annotate(num_review=Count("review")).order_by(
                    "-num_review"
                )
            else:
                queryset = queryset.annotate(num_review=Count("review")).order_by(
                    "num_review"
                )
        elif sort_field == "price":
            if sort_type == "dec":
                queryset = queryset.order_by("-price")
            else:
                queryset = queryset.order_by("price")
        elif sort_field == "date":
            if sort_type == "dec":
                queryset = queryset.order_by("-date")
            else:
                queryset = queryset.order_by("date")
        data = {}
        current_page = int(request.query_params.get("currentPage", 1))
        data["currentPage"] = current_page
        result_page = self.paginate_queryset(queryset, request, view=self)
        serializer = ProductSerializer(result_page, many=True)
        data["items"] = serializer.data
        data["lastPage"] = self.page.paginator.num_pages

        return Response(data=data, status=200)


class PopularProductView(APIView):
    def get(self, request) -> Response:
        queryset = (
            Product.objects.annotate(
                num_review=Count("review", filter=Q(review__is_checked=True)),
                avg_rating=Avg("review__rate", filter=Q(review__is_checked=True)),
            )
            .order_by("-num_review", "-avg_rating")[:8]
            .prefetch_related("images")
        )
        serialized = ProductSerializer(queryset, many=True)
        return Response(data=serialized.data, status=200)


class LimitedProduct(APIView):
    def get(self, request: Request) -> Response:
        queryset: QuerySet = Product.objects.filter(limited=True)[:5].prefetch_related(
            "images"
        )
        serialized = ProductSerializer(queryset, many=True)
        return Response(data=serialized.data, status=200)


class SalesView(APIView, PageNumberPagination):
    page_size = 3

    page_query_param = "currentPage"
    page_size_query_param = "limit"
    max_page_size = 1000

    def get(self, request: Request) -> Response:
        queryset: QuerySet = Product.objects.filter(sale__isnull=False).order_by("id")
        data = {}
        current_page = int(request.query_params.get("currentPage", 1))
        data["currentPage"] = current_page
        result_page = self.paginate_queryset(queryset, request, view=self)
        serializer = ProductSaleSerializer(result_page, many=True)
        data["items"] = serializer.data
        data["lastPage"] = self.page.paginator.num_pages

        return Response(data=data, status=200)


class BannerProduct(APIView):
    def get(self, request: Request) -> Response:
        queryset = Product.objects.all().order_by("?")[:5].prefetch_related("images")
        serialized = ProductSerializer(queryset, many=True)
        return Response(data=serialized.data, status=200)


class ProductDetailView(APIView):
    def get(self, request: Request, pk) -> Response:
        product = Product.objects.get(id=pk)
        if product:
            return Response(data=ProductSerializer(product).data, status=200)
        return Response(status=404)


class TagView(APIView):
    def get(self, request: Request) -> Response:
        req_category = self.request.query_params.get("category")
        if req_category:
            req_category = Category.objects.get(
                id=self.request.query_params.get("category")
            )
            if not req_category.parent:
                child_category = Category.objects.filter(parent=req_category)
                child_tag = Tag.objects.filter(category__in=list(child_category))
                tags = child_tag.all()
            else:
                self_tags = req_category.tags
                tags = self_tags.all()
        else:
            tags = Tag.objects.all()
        return Response(TagSerializer(tags, many=True).data, status=200)


class ReviewView(APIView):
    def post(self, request: Request, pk) -> Response:
        serialized = ReviewSerializer(data=request.data)
        if serialized.is_valid():
            product = Product.objects.get(pk=pk)
            Review.objects.create(product=product, **serialized.data)
            checked_review = Review.objects.filter(product=product, is_checked=True)
            new_rating = checked_review.aggregate(Avg("rate")).get("rate__avg")
            if new_rating:
                product.rating = new_rating
                product.save()
            return Response(
                data=ReviewSerializer(checked_review, many=True).data, status=200
            )
        return Response(status=400)
