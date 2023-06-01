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
# router.register(r'shops', ShopView)
# router.register(r'categories', CategoryView)
# router.register(r'products', ProductsInfoView,
#                 basename='products')

urlpatterns = [
    # path('partner/update', PartnerUpdate.as_view(),
    #      name='partner-update'),
    # path('partner/state', PartnerState.as_view(),
    #      name='partner-state'),
    # path('partner/orders', PartnerOrders.as_view(),
    #      name='partner-orders'),
    # path('user/register', RegisterAccount.as_view(),
    #      name='user-register'),
    # path('user/register/confirm', ConfirmAccount.as_view(),
    #      name='user-register-confirm'),
    # path('user/details', AccountDetails.as_view(),
    #      name='user-details'),
    # path('user/contact', ContactView.as_view(),
    #      name='user-contact'),
    # path('user/login', LoginAccount.as_view(),
    #      name='user-login'),
    # path('user/password_reset', reset_password_request_token,
    #      name='password-reset'),
    # path('user/password_reset/confirm', reset_password_confirm,
    #      name='password-reset-confirm'),
    # path('basket', BasketView.as_view(),
    #      name='basket'),
    # path('order', OrderView.as_view(),
    #      name='order'),
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
