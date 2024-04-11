import decimal
from _decimal import Decimal
from typing import Dict, Type, Union

from django.db.models import Avg, QuerySet
from django.utils.timezone import now
from rest_framework import serializers as s

from .models import (
    Category,
    CategoryImage,
    Product,
    ProductImage,
    Tag,
    Review,
    Specification,
)


class CategoryImageSerializer(s.ModelSerializer):
    src = s.SerializerMethodField()

    class Meta:
        model = CategoryImage
        fields = ["src", "alt"]

    def get_src(self, obj: CategoryImage) -> str:
        return obj.src.url


class CategorySerializer(s.ModelSerializer):
    image = CategoryImageSerializer()
    subcategories = s.SerializerMethodField()

    def get_subcategories(self, category: Category):
        subcategory = Category.objects.filter(parent=category).all()
        if subcategory:
            return CategorySerializer(subcategory, many=True).data
        return None

    class Meta:
        model = Category
        fields = ["id", "title", "image", "subcategories"]


class ProductImageSerializer(s.ModelSerializer):
    src = s.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ["src", "alt"]

    def get_src(self, obj: ProductImage) -> str:
        return obj.src.url


class TagSerializer(s.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class ReviewSerializer(s.ModelSerializer):
    date = s.DateTimeField(format="%Y-%m-%d %H:%M", default=now)

    class Meta:
        model = Review
        fields = ["email", "rate", "date", "text", "author"]


class SpecificationsSerializer(s.ModelSerializer):
    class Meta:
        model = Specification
        fields = ["name", "value"]


class ProductSerializer(s.ModelSerializer):
    category = s.SerializerMethodField()
    reviews = s.SerializerMethodField()
    images = ProductImageSerializer(many=True)
    tags = s.SerializerMethodField()
    fullDescription = s.CharField(source="description")
    description = s.SerializerMethodField()
    specifications = s.SerializerMethodField()
    rating = s.SerializerMethodField()
    # price = s.SerializerMethodField()

    def get_rating(self, obj: Product) -> QuerySet[Review]:
        return (
            Review.objects.filter(product=obj).aggregate(Avg("rate")).get("rate__avg")
        )

    def get_specifications(self, obj: Product) -> Dict:
        return SpecificationsSerializer(
            Specification.objects.filter(product=obj), many=True
        ).data

    def get_description(self, obj: Product) -> str:
        return obj.description[:10]

    def get_reviews(self, obj: Product) -> Dict:
        reviews = Review.objects.filter(product=obj, is_checked=True)
        reviews_serialized = ReviewSerializer(reviews, many=True)
        return reviews_serialized.data

    def get_category(self, obj: Product) -> Type[int]:
        return obj.category_id

    def get_tags(self, obj: Product) -> Union[None, Dict]:
        if obj.category.parent:
            parent_tags = obj.category.parent.tags
            self_tags = obj.category.tags
            tags = parent_tags.all() | self_tags.all()
            if tags:
                return TagSerializer(tags, many=True).data

    class Meta:
        model = Product
        fields = [
            "id",
            "category",
            "price",
            "count",
            "date",
            "title",
            "fullDescription",
            "freeDelivery",
            "images",
            "tags",
            "reviews",
            "rating",
            "description",
            "specifications",
        ]


class ProductSaleSerializer(s.ModelSerializer):
    salePrice = s.SerializerMethodField()
    dateFrom = s.SerializerMethodField()
    dateTo = s.SerializerMethodField()
    images = ProductImageSerializer(many=True)
    price = s.SerializerMethodField()

    def get_price(self, obj: Product) -> str:
        return "%.2f" % Decimal(obj.price / (1 - obj.sale.salePrice/100)).quantize(
                                    Decimal("0.01"), decimal.ROUND_HALF_UP)

    def get_salePrice(self, obj: Product) -> str:
        return "%.2f" % obj.price

    def get_dateFrom(self, obj: Product) -> str:
        return obj.sale.dateFrom.strftime("%m-%d")

    def get_dateTo(self, obj: Product) -> str:
        return obj.sale.dateTo.strftime("%m-%d")

    class Meta:
        model = Product
        fields = ["id", "price", "salePrice", "dateFrom", "dateTo", "title", "images"]