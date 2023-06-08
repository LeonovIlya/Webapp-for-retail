from django.urls import path, include, re_path

from .views import ChangePasswordView, ConfirmEmailView, LoginView, \
    OrderView, ProfileView, RegistrationView, ResetPasswordView, \
    passwordResetConfirm, logout_request, confirm_email

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
         passwordResetConfirm,
         name='reset_password_confirm')
]
