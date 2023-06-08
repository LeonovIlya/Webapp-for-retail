from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Sum, Q
from django.db.utils import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.http import urlsafe_base64_decode

from rest_framework.decorators import permission_classes
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response

from .forms import RegisterForm, SetPasswordForm, ResetPasswordForm
from .models import ConfirmEmailToken, Comment, Contact, User
from .serializers import UserRegSerializer, ContactSerializer
from .tokens import account_activation_token

from backend.models import Order, OrderItem, Product, ProductInfo, Shop

from shop.task import send_email_to_confirm_user_email, \
    send_email_to_reset_password


class LoginView(APIView):
    template_name = 'login.html'

    @staticmethod
    def get(request, *args, **kwargs):
        return Response()

    @staticmethod
    def post(request, *args, **kwargs):
        email = request.data['email']
        password = request.data['password']
        user = authenticate(email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('backend:index')
        else:
            messages.error(request, 'Username or password not correct!')
            return redirect('authorization:login')


class RegistrationView(APIView):
    template_name = 'register.html'

    @staticmethod
    def get(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('authorization:profile')
        else:
            form = RegisterForm()
            data = {
                'form': form
            }
            return Response(data)

    @staticmethod
    def post(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('authorization:profile')
        else:
            form = RegisterForm(request.POST or None)
            if form.is_valid():
                user = form.save(commit=False)
                user.username = user.username.lower()
                user.save()
                Contact.objects.create(user=user)
                messages.success(request, 'You have registered successfully!')
                login(request, user)
                return redirect('backend:index')
            else:
                data = {
                     'form': form
                 }
                return Response(data)


class ConfirmEmailView(LoginRequiredMixin, APIView):
    def get(self, request, token, *args, **kwargs):
        try:
            confirmed_token = ConfirmEmailToken.objects.get(
                user=self.request.user.id,
                key=token,
                used=False)
            confirmed_token.user.email_confirmed = True
            confirmed_token.user.save()
            confirmed_token.used = True
            confirmed_token.save()
            messages.success(request, 'Email successfully confirmed!')

        except ConfirmEmailToken.DoesNotExist:
            messages.error(request, 'Something wrong, please try again!')
        return redirect('authorization:profile')


class ProfileView(LoginRequiredMixin, APIView):
    template_name = 'profile.html'

    def get(self, request, *args, **kwargs):
        try:
            cart_count = Order.objects.filter(status='new').values_list(
                'total_items_count', flat=True).get(user=self.request.user)
        except (Order.DoesNotExist, TypeError):
            cart_count = None

        user = User.objects.get(id=self.request.user.id)
        contact = Contact.objects.get(user=self.request.user)
        orders = Order.objects.filter(user=self.request.user)
        reviews = Comment.objects.filter(user=self.request.user).order_by(
            '-posted')

        data = {
            'cart_count': cart_count,
            'user': user,
            'contact': contact,
            'orders': orders,
            'reviews': reviews
        }
        return Response(data)

    def post(self, request, *args, **kwargs):

        username = request.POST.get('username')
        email = request.POST.get('email')
        shop_name = request.POST.get('shop_name')
        shop_url = request.POST.get('shop_url')
        company = request.POST.get('company')
        position = request.POST.get('position')
        contact_city = request.POST.get('contact_city')
        contact_street = request.POST.get('contact_street')
        contact_house = request.POST.get('contact_house')
        contact_structure = request.POST.get('contact_structure')
        contact_building = request.POST.get('contact_building')
        contact_apartment = request.POST.get('contact_apartment')
        contact_phone = request.POST.get('contact_phone')

        try:
            user = User.objects.get(id=self.request.user.id)
        except User.DoesNotExist:
            messages.error(request, 'Something WRONG!')
            return redirect('authorization:profile')

        contact = Contact.objects.get(user=self.request.user)

        if self.request.user.type == 'shop':
            try:
                shop = Shop.objects.get(user=self.request.user)
            except Shop.DoesNotExist:
                shop = Shop.objects.create(user=self.request.user)
            if shop_url:
                shop.url = shop_url
            if shop_name:
                shop.name = shop_name
            try:
                shop.save()
            except IntegrityError as e:
                messages.error(request, e)
                return redirect('authorization:profile')

        if username:
            user.username = username
        if email:
            user.email = email
            user.email_confirmed = False
        if company:
            user.company = company
        if position:
            user.position = position
        try:
            user.save()
        except IntegrityError as e:
            messages.error(request, e)
            return redirect('authorization:profile')

        if contact_city:
            contact.city = contact_city
        if contact_street:
            contact.street = contact_street
        if contact_house:
            contact.house = contact_house
        if contact_structure:
            contact.structure = contact_structure
        if contact_building:
            contact.building = contact_building
        if contact_apartment:
            contact.apartment = contact_apartment
        if contact_phone:
            contact.phone = contact_phone
        try:
            contact.save()
        except IntegrityError as e:
            messages.error(request, e)
            return redirect('authorization:profile')

        messages.success(request, 'You have change profile successfully!')
        return redirect('authorization:profile')


class ChangePasswordView(LoginRequiredMixin, APIView):
    template_name = 'account/change_password.html'

    def get(self, request, *args, **kwargs):
        form = SetPasswordForm(self.request.user)
        data = {
            'form': form
        }
        return Response(data)

    def post(self, request, *args, **kwargs):
        form = SetPasswordForm(self.request.user, request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your password has been changed '
                                      'successfully!\nPlease login with new '
                                      'password!')
            return redirect('authorization:login')
        else:
            data = {
                'form': form
            }
        return Response(data)


class ResetPasswordView(APIView):
    template_name = 'account/reset_password.html'

    def get(self, request, *args, **kwargs):
        form = ResetPasswordForm()
        data = {
            'form': form
        }
        return Response(data)
    def post(self, request, *args, **kwargs):
        form = ResetPasswordForm(request.POST or None)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(Q(email=email)).first()
            if user:
                send_email_to_reset_password.delay(email)
                messages.success(request, 'Check your email!')
            else:
                messages.error(request, 'Wrong email!')
        data = {
            'form': form
        }
        return Response(data)

class OrderView(LoginRequiredMixin, APIView):
    template_name = 'order.html'

    def get(self, request, order_id, *args, **kwargs):
        order = get_object_or_404(Order,
                                  id=order_id,
                                  user=self.request.user)
        products = OrderItem.objects.filter(order=order)
        total_price = OrderItem.objects.filter(order=order).aggregate(
            Sum('total_price'))
        try:
            cart_count = Order.objects.filter(status='new').values_list(
                'total_items_count', flat=True).get(user=self.request.user)
        except (Order.DoesNotExist, TypeError):
            cart_count = None

        data = {
            'order': order,
            'products': products,
            'total_price': total_price,
            'cart_count': cart_count
        }
        return Response(data)

@login_required
def logout_request(request):
    logout(request)
    return redirect('backend:index')

@login_required
def confirm_email(request, user_id):
    send_email_to_confirm_user_email.delay(user_id)
    messages.success(request, 'Check your mail!')
    return redirect('authorization:profile')

def passwordResetConfirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your password has been set. You may go ahead and <b>log in </b> now.")
                return redirect('authorization:login')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)

        form = SetPasswordForm(user)
        return render(request, 'account/reset_password_confirm.html', {'form':
                                                                      form})
    else:
        messages.error(request, "Link is expired")

    messages.error(request, 'Something went wrong, redirecting back to Homepage')
    return redirect('authorization:login')
