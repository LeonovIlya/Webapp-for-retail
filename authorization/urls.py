from django.urls import path, include, re_path
from django_rest_passwordreset.views import reset_password_request_token,\
    reset_password_confirm
from .views import RestrictedApiView, RegistrationView, ContactView, \
    LoginView, logout_request


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
]