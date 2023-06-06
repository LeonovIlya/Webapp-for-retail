from django_rest_passwordreset.views import reset_password_request_token,\
    reset_password_confirm
from django.urls import path, include, re_path

from .views import LoginView, OrderView, ProfileView, RegistrationView, \
    logout_request, send_email


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
    path('profile/order/<int:order_id>/', OrderView.as_view(),
         name='show_order'),
    path('register', RegistrationView.as_view(),
         name='register'),
    path('confirm_email/<int:user_id>', send_email,
         name='confirm_email')
]