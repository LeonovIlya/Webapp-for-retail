from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import Comment, Contact, User


@admin.register(User)
class UserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('username', 'company', 'position',
                                         'type')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('id', 'email', 'username', 'type', 'company',
                    'is_active', 'is_staff', 'is_superuser')
    list_filter = ['type', 'is_active']
    search_fields = ('email', 'username')
    ordering = ('email',)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'city', 'street', 'house', 'structure',
                    'building', 'apartment', 'phone']
    list_filter = ['city', 'street']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'text', 'product', 'rating', 'posted')
    list_filter = ('user', 'product' )
    search_fields = ('user', 'product')
