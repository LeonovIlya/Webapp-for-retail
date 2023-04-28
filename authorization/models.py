from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django_rest_passwordreset.tokens import get_token_generator
from .managers import UserManager


USER_TYPE_CHOICES = (
    ('shop', 'Магазин'),
    ('buyer', 'Покупатель'),
    ('manager', 'Менеджер'),
    ('admin', 'Администратор'))


class User(AbstractBaseUser, PermissionsMixin):

    REQUIRED_FIELDS = []
    objects = UserManager()
    USERNAME_FIELD = 'email'
    email = models.EmailField(verbose_name='Email',
                              unique=True)
    company = models.CharField(verbose_name='Компания',
                               max_length=40,
                               blank=True)
    position = models.CharField(verbose_name='Должность',
                                max_length=40,
                                blank=True)
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _('username'),
        max_length=150,
        help_text=_('Required. 150 characters or fewer. Letters, digits and '
                    '@/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active.'
            'Unselect this instead of deleting accounts.'
        ),
    )
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    type = models.CharField(verbose_name='Тип пользователя',
                            choices=USER_TYPE_CHOICES,
                            max_length=7,
                            default='buyer')
    date_joined = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Список пользователей'
        ordering = ('id',)

    def __str__(self):
        return f'{self.email}'


class Contact(models.Model):
    user = models.ForeignKey(User,
                             verbose_name='Пользователь',
                             related_name='contacts',
                             blank=True,
                             on_delete=models.CASCADE)

    city = models.CharField(max_length=50,
                            verbose_name='Город',
                            blank=True)
    street = models.CharField(max_length=100,
                              verbose_name='Улица',
                              blank=True)
    house = models.CharField(max_length=15,
                             verbose_name='Дом',
                             blank=True)
    structure = models.CharField(max_length=15,
                                 verbose_name='Корпус',
                                 blank=True)
    building = models.CharField(max_length=15,
                                verbose_name='Строение',
                                blank=True)
    apartment = models.CharField(max_length=15,
                                 verbose_name='Квартира',
                                 blank=True)
    phone = models.CharField(max_length=40,
                             verbose_name='Телефон',
                             blank=True)

    class Meta:
        verbose_name = 'Контакты пользователя'
        verbose_name_plural = 'Список контактов пользователя'

    def __str__(self):
        return f'{self.city}, ул.{self.street}, дом {self.house}' \
               f' ({self.phone})'


class ConfirmEmailToken(models.Model):
    class Meta:
        verbose_name = 'Токен подтверждения Email'
        verbose_name_plural = 'Токены подтверждения Email'

    @staticmethod
    def generate_key():
        return get_token_generator().generate_token()

    user = models.ForeignKey(
        User,
        related_name='confirm_email_tokens',
        on_delete=models.CASCADE,
        verbose_name=_('The User which is associated to this password reset '
                       'token')
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('When was this token generated')
    )

    key = models.CharField(
        _('Key'),
        max_length=64,
        db_index=True,
        unique=True
    )

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(ConfirmEmailToken, self).save(*args, **kwargs)

    def __str__(self):
        return 'Password reset token for user {user}'.format(user=self.user)
