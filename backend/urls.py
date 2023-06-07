from django.contrib.auth import logout
from django.conf import settings
from django_rest_passwordreset.views import reset_password_request_token,\
    reset_password_confirm
from django.urls import path, include
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns

from .views import CartView, IndexView, ProductInfoView, add_to_cart,\
    remove_from_cart, search

app_name = 'backend'

router = routers.SimpleRouter()

urlpatterns = [
    path('', IndexView.as_view(),
         name='index'),
    path('product/<int:product_id>', ProductInfoView.as_view(),
         name='product_info'),
    path('remove_from_cart/<int:item_id>', remove_from_cart,
         name='remove_from_cart'),
    path('add_to_cart/<int:product_id>', add_to_cart,
         name='add_to_cart'),
    path('cart', CartView.as_view(),
         name='cart'),
    path('search/', search, name='search'),
]

urlpatterns += router.urls
