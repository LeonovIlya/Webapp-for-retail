from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver, Signal
from django_rest_passwordreset.signals import reset_password_token_created

from authorization.models import ConfirmEmailToken, User


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token,
                                 **kwargs):
    msg = EmailMultiAlternatives(
        # title:
        f"Password Reset Token for {reset_password_token.user}",
        # message:
        reset_password_token.key,
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [reset_password_token.user.email]
    )
    msg.send()


def confirm_email_registered_signal(user_id, **kwargs):
    token, _ = ConfirmEmailToken.objects.get_or_create(user_id=user_id)
    print(token)

    msg = EmailMultiAlternatives(
        # title:
        f"Token for confirmation{token.user.email}",
        # message:
        token.key,
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [token.user.email]
    )
    msg.send()


def new_order_signal(user_id, **kwargs):
    user = User.objects.get(id=user_id)
    msg = EmailMultiAlternatives(
        # title:
        f"Обновление статуса заказа",
        # message:
        'Заказ сформирован',
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [user.email]
    )
    msg.send()
