from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


from authorization.models import ConfirmEmailToken, User
from backend.models import Order, OrderItem
from authorization.tokens import account_activation_token


def reset_password_signal(email, **kwargs):
    user = User.objects.filter(Q(email=email)).first()
    msg_body = render_to_string('account/template_reset_password.html', {
                'username': user.username,
                'domain': '127.0.0.1:8000',
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
                "protocol": 'http'
                })
    msg = EmailMultiAlternatives(
        # title:
        'Password Reset request',
        # message:
        'text',
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [user.email]
    )
    msg.attach_alternative(msg_body, "text/html")
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
