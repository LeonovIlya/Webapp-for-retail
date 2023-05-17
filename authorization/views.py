from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.shortcuts import render, redirect
from rest_framework.decorators import permission_classes
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response

from .models import Contact
from .serializers import UserRegSerializer, ContactSerializer

from backend.models import Order, OrderItem


def profileView(request):
    template = 'accounts/index.html'
    context = {'user': request.user}
    return render(request, template, context)


@permission_classes([IsAuthenticated, ])
class RestrictedApiView(APIView):
    def get(self, request, *args, **kwargs):
        if request.user.type == 'buyer':
            data = f'{request.user}, Вы покупатель'
        elif request.user.type == 'shop':
            data = f'{request.user}, Вы продавец'
        return Response(data)


class RegistrationView(APIView):
    def post(self, request):
        serializer = UserRegSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            user = serializer.save()
            data['response'] = 'Successfully created a new User'
            data['user'] = user.email
        else:
            data = serializer.errors
        return Response(data)


@permission_classes([IsAuthenticated])
class ContactView(APIView):
    def get(self, request):
        try:
            contact = Contact.objects.get(user=request.user)
            serializer = ContactSerializer(contact)
        except:
            return Response({'response': f'{request.user} has no contacts. '
                                         f'You can make PUT request'})
        return Response(serializer.data)

    def put(self, request):
        contact, _ = Contact.objects.get_or_create(user=request.user)
        serializer = ContactSerializer(contact, request.data)
        if serializer.is_valid():
            serializer.save()
        else:
            raise serializer.errors
        return Response(serializer.data)


class LoginView(APIView):
    template_name = 'login.html'

    def get(self, request, *args, **kwargs):
        return Response()

    def post(self, request,  *args, **kwargs):
        email = request.data['email']
        password = request.data['password']
        user = authenticate(email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('backend:index')
        else:
            messages.error(request, 'Username or password not correct!')
            return redirect('authorization:login')


class ProfileView(LoginRequiredMixin, APIView):
    template_name = 'profile.html'

    def get(self, request, *args, **kwargs):

        try:
            cart_count = Order.objects.filter(status='new').values_list(
                'total_items_count', flat=True).get(user=self.request.user)
        except Order.DoesNotExist:
            cart_count = None

        data = {
            'order': order,
            'cart_count': cart_count
        }
        return Response(data)


class CartView(LoginRequiredMixin, APIView):
    template_name = 'cart.html'

    def get(self, request, *args, **kwargs):
        try:
            order = Order.objects.filter(status='new', is_active=True).get(
                user=self.request.user)
            products = OrderItem.objects.filter(order=order)
            total_price = OrderItem.objects.filter(order=order).aggregate(
                Sum('total_price'))

            try:
                cart_count = Order.objects.filter(status='new').values_list(
                    'total_items_count', flat=True).get(user=self.request.user)
            except Order.DoesNotExist:
                cart_count = None

            data = {
                'order': order,
                'products': products,
                'total_price': total_price,
                'cart_count': cart_count
            }
            return Response(data)

        except ObjectDoesNotExist:
            messages.error(request, 'You do not have an active order!')
            return Response()

    def post(self, request, *args, **kwargs):
        pass


@login_required
def logout_request(request):
    logout(request)
    return redirect('backend:index')


@login_required
def remove_from_cart(request, item_id):
    try:
        order = Order.objects.filter(status='new', is_active=True).get(
            user=request.user)
        try:
            product = OrderItem.objects.filter(order=order).get(id=item_id)
            product.delete()
            return redirect('authorization:cart')
        except ObjectDoesNotExist:
            messages.error(request, 'Something WRONG!')
            return redirect('authorization:cart')
    except ObjectDoesNotExist:
        messages.error(request, 'Something WRONG!')
        return redirect('authorization:cart')


@login_required
def place_order(request):
    try:
        order = Order.objects.filter(status='new', is_active=True).get(
            user=request.user)
        order.status = 'ordered'
        order.save()
        return redirect('authorization:cart')
    except ObjectDoesNotExist:
        messages.error(request, 'Something WRONG!')
        return redirect('authorization:cart')



