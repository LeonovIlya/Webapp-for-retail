from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, \
    SetPasswordForm
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox

from .models import User

USER_TYPE_CHOICES = (
    ('shop', 'Магазин'),
    ('buyer', 'Покупатель'))


class RegisterForm(UserCreationForm):
    type = forms.ChoiceField(widget=forms.RadioSelect,
                             choices=USER_TYPE_CHOICES)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'type')

    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())


class ChangePasswordForm(SetPasswordForm):
    class Meta:
        model = User
        fields = ('new_password1', 'new_password2')


class ResetPasswordForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)

    # captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())
