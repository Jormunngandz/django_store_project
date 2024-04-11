from django.urls import path
from .views import \
    CategoriesView, CatalogView, PopularProductView, LimitedProduct, BannerProduct, ProductDetailView, TagView, \
    ReviewView, SalesView

urlpatterns = [

    path('categories/', CategoriesView.as_view(), name='categories'),
    path('catalog/', CatalogView.as_view(), name='catalog'),
    path('products/popular', PopularProductView.as_view(), name='popular_product'),
    path('products/limited', LimitedProduct.as_view(), name='limited_product'),
    path('banners', BannerProduct.as_view(), name='banners_product'),
    path('product/<int:pk>/reviews', ReviewView.as_view(), name='reviews'),
    path('product/<int:pk>', ProductDetailView.as_view(), name='product_detail'),
    path('tags', TagView.as_view(), name='tag_list'),
    path('sales', SalesView.as_view(), name='sales'),




]
