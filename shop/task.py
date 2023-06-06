from shop.celery import app
from .service import confirm_email_registered_signal, new_order_signal


@app.task
def send_email_test(user_id):
    confirm_email_registered_signal(user_id)
