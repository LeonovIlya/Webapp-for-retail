from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver, Signal
from django_rest_passwordreset.signals import reset_password_token_created
from django.template import Context
from django.template.loader import render_to_string
from authorization.models import ConfirmEmailToken, User
from backend.models import Order, OrderItem


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
    token, _ = ConfirmEmailToken.objects.get_or_create(user_id=user_id,
                                                       used=False)
    msg = EmailMultiAlternatives(
        # title:
        'Please confirm your email to complete registration',
        # message:
        f'http://127.0.0.1:8000/auth/profile/confirm_email/{token.key}',
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [token.user.email]
    )
    msg.send()


def new_order_signal(user_id, order_id, **kwargs):
    user = User.objects.get(id=user_id)
    order = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order=order)

    context = {
        'order': order,
        'order_items': order_items
    }
    html_body = render_to_string('email/order_placed.html', context=context)

    msg = EmailMultiAlternatives(
        # title:
        'Order status update',
        # message:
        'text',
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [user.email]
    )
    msg.attach_alternative(html_body, "text/html")
    msg.send()
