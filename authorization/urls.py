from django.urls import path, include, re_path
from django_rest_passwordreset.views import reset_password_request_token,\
    reset_password_confirm
from .views import CartView, ContactView, LoginView, OrderView, ProfileView,\
    RestrictedApiView, RegistrationView, add_to_cart, logout_request, \
    place_order, remove_from_cart


urlpatterns = [
    # path('', include('djoser.urls')),
    # path('', include('djoser.urls.authtoken')),
    # path('', include('rest_framework.urls')),
    # path('reg/', RegistrationView.as_view(),
    #      name='register'),
    # path('password_reset', reset_password_request_token,
    #      name='password-reset'),
    # path('password_reset/confirm', reset_password_confirm,
    #      name='password-reset-confirm'),
    # path('restricted/', RestrictedApiView.as_view()),
    # path('contact/', ContactView.as_view()),
    re_path(r'^login/$', LoginView.as_view(),
            name='login'),
    path('logout', logout_request,
         name='logout'),
    path('profile', ProfileView.as_view(),
         name='profile'),
    path('cart', CartView.as_view(),
         name='cart'),
    path('remove_from_cart/<int:item_id>', remove_from_cart,
         name='remove_from_cart'),
    path('place_order', place_order,
         name='place_order'),
    path('add_to_cart/<int:product_id>', add_to_cart,
         name='add_to_cart'),
    path('profile/order/<int:order_id>/', OrderView.as_view(),
         name='show_order')
]