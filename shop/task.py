from django.core.exceptions import ObjectDoesNotExist

from shop.celery import app
from .service import confirm_email_registered_signal, new_order_signal, \
    reset_password_signal


@app.task(ignore_result=False)
def send_email_to_confirm_user_email(user_id):
    confirm_email_registered_signal(user_id)
    return 'Success'


@app.task(ignore_result=False)
def send_email_order_placed(user_id, order_id):
    new_order_signal(user_id, order_id)
    return 'Success'


@app.task(ignore_result=False)
def send_email_to_reset_password(email):
    reset_password_signal(email)
    return 'Success'
