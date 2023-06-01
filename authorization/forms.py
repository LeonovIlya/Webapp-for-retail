from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Comment, User

USER_TYPE_CHOICES = (
    ('shop', 'Магазин'),
    ('buyer', 'Покупатель'))


class UserAdminCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ['email', 'type', 'company', 'position']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'rating': forms.RadioSelect()
        }


class RegisterForm(UserCreationForm):
    type = forms.ChoiceField(widget=forms.RadioSelect,
                             choices=USER_TYPE_CHOICES)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'type')
