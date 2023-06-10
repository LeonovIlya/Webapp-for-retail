from django.urls import path, include

from .views import ChangePasswordView, ConfirmEmailView, LoginView, \
    OrderView, ProfileView, RegistrationView, ResetPasswordView, \
    confirm_email, logout_request, reset_password_confirm

urlpatterns = [
    path('login', LoginView.as_view(),
         name='login'),
    path('logout', logout_request,
         name='logout'),
    path('profile', ProfileView.as_view(),
         name='profile'),
    path('profile/order/<int:order_id>', OrderView.as_view(),
         name='show_order'),
    path('register', RegistrationView.as_view(),
         name='register'),
    path('profile/confirm_email/<int:user_id>', confirm_email,
         name='confirm_email'),
    path('profile/confirm_email/<token>', ConfirmEmailView.as_view(),
         name='confirmation'),
    path('profile/change_password', ChangePasswordView.as_view(),
         name='change_password'),
    path('profile/reset_password', ResetPasswordView.as_view(),
         name='reset_password'),
    path('profile/reset_password/<uidb64>/<token>',
         reset_password_confirm,
         name='reset_password_confirm')
]
