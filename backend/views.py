from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.password_validation import validate_password
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import IntegrityError
from django.db.models import Q, Sum, F, Avg, Max, Min
from django.db.models.query import Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from rest_framework import status, viewsets
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.authtoken.models import Token

from yaml import load as load_yaml, Loader
from ujson import loads as load_json
from distutils.util import strtobool
from requests import get

from .models import Category, Shop, ProductInfo, Order, OrderItem, Product, \
    Parameter, Brand
from authorization.forms import CommentForm
from authorization.models import Contact, ConfirmEmailToken, Comment, User
from authorization.serializers import CommentSerializer
from shop.task import send_email_order_placed
from .serializers import CategorySerializer, ShopSerializer, \
    ProductInfoSerializer, OrderSerializer, OrderItemSerializer, \
    UserSerializer, ContactSerializer, ProductSerializer

class IndexView(APIView):
    template_name = 'store.html'

    def get(self, request, *args, **kwargs):

        price_min_abs = ProductInfo.objects.aggregate(Min('price'))[
            'price__min']
        price_max_abs = ProductInfo.objects.aggregate(Max('price'))[
            'price__max']

        category_vars = set(request.GET.getlist('category'))
        brand_vars = set(request.GET.getlist('brand'))
        price_min = int(request.GET.get('min_price', price_min_abs))
        price_max = int(request.GET.get('max_price', price_max_abs))
        paginate_by = int(request.GET.get('paginate_by', 20))
        sort_by = str(request.GET.get('sort_by', 'id'))
        page = int(request.GET.get('page', 1))

        categories = Category.objects.all()
        brands = Brand.objects.all()
        products = ProductInfo.objects.all()

        if category_vars:
            products = products.filter(category__in=category_vars)
        if brand_vars:
            products = products.filter(brand__in=brand_vars)

        products = products.filter(price__range=(price_min, price_max))

        try:
            cart_count = Order.objects.filter(status='new').values_list(
                'total_items_count', flat=True).get(user=self.request.user)
        except (Order.DoesNotExist, TypeError):
            cart_count = None

        sorted_products = products.order_by(sort_by)
        paginator = Paginator(sorted_products, paginate_by)

        try:
            products_info = paginator.get_page(page)
        except PageNotAnInteger:
            products_info = paginator.get_page(1)
        except EmptyPage:
            products_info = paginator.page(paginator.num_pages)

        data = {
            'products': products,
            'products_info': products_info,
            'categories': categories,
            'brands': brands,
            'paginate_by': paginate_by,
            'sort_by': sort_by,
            'cart_count': cart_count,
            'price_min': price_min,
            'price_max': price_max,
            'price_min_abs': price_min_abs,
            'price_max_abs': price_max_abs,
            'category_vars': category_vars,
            'brand_vars': brand_vars
        }
        return Response(data)


class ProductInfoView(APIView):
    template_name = 'product.html'

    def get(self, request, product_id, *args, **kwargs):
        product_info = get_object_or_404(ProductInfo,
                                         product_id=product_id)
        parameters = Product.parameters.through.objects.filter(
            product_id=product_id)
        comments = Comment.objects.filter(product_id=product_id).order_by(
            '-posted')

        try:
            cart_count = Order.objects.filter(status='new').values_list(
                'total_items_count', flat=True).get(user=self.request.user)
        except (Order.DoesNotExist, TypeError):
            cart_count = None

        data = {
            'product_info': product_info,
            'parameters': parameters,
            'comments': comments,
            'cart_count': cart_count
        }
        return Response(data)



    def post(self, request, *args, **kwargs):
        if request.POST.get('form_name') == 'add_review':
            product_id = int(request.data['product'])
            text = str(request.POST.get('text'))
            rating = int(request.POST.get('rating'))

            if not text:
                messages.error(request, 'Need text to add review')
                return redirect("backend:product_info",
                                product_id=product_id)
            if not rating:
                messages.error(request, 'Need rating to add review')
                return redirect("backend:product_info",
                                product_id=product_id)

            new_comment = Comment.objects.create(
                user=self.request.user,
                text=text,
                product=Product.objects.get(id=product_id),
                rating=rating)
            new_comment.save()
            return redirect("backend:product_info",
                            product_id=product_id)

        elif request.POST.get('form_name') == 'add_to_cart':
            product_id = int(request.POST.get('product'))
            quantity = int(request.POST.get('quantity'))
            add_to_cart(request=request,
                        product_id=product_id,
                        quantity=quantity)
            return redirect("backend:product_info",
                            product_id=product_id)


class CartView(LoginRequiredMixin, APIView):
    template_name = 'cart.html'

    def get(self, request, *args, **kwargs):
        try:
            order = Order.objects.filter(status='new', is_active=True).get(
                user=self.request.user)
            products = OrderItem.objects.filter(order=order).order_by('id')
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

        except Order.DoesNotExist:
            messages.error(request, 'You do not have an active order!')
            return Response()

    def post(self, request, *args, **kwargs):
        if request.POST.get('form_name') == 'change_quantity':
            product_id = int(request.POST.get('product_id'))
            quantity = int(request.POST.get('quantity'))

            try:
                order = Order.objects.filter(status='new',
                                             is_active=True).get(
                    user=self.request.user)
            except Order.DoesNotExist:
                messages.error(request, 'Order does not found! Please try '
                                        'again!')
                return redirect('backend:cart')

            try:
                order_item = OrderItem.objects.filter(order=order).get(
                    product=product_id)
            except OrderItem.DoesNotExist:
                messages.error(request, 'Product does not found in your cart! '
                                        'Please try again!')
                return redirect('backend:cart')

            try:
                product = ProductInfo.objects.get(product=product_id)
            except Product.DoesNotExist:
                messages.error(request, 'Product does not found! '
                                        'Please try again!')
                return redirect('backend:cart')

            if quantity <= product.quantity:
                order_item.quantity = quantity
                order_item.save()
                return redirect('backend:cart')
            else:
                messages.error(request, 'SORRY, OUT OF STOCK OR TO MANY!')
                return redirect('backend:cart')
        elif request.POST.get('form_name') == 'place_order':
            try:
                order = Order.objects.filter(status='new',
                                             is_active=True).get(
                    user=self.request.user)
                order_items = OrderItem.objects.filter(order=order)

                for order_item in order_items:
                    product = ProductInfo.objects.get(product=order_item.product)
                    if order_item.quantity > product.quantity:
                        messages.error(request,
                                       f'SORRY, "{order_item.product.name}" '
                                       f'OUT OF STOCK OR TO MANY!')
                        return redirect('backend:cart')
                    else:
                        product.quantity -= order_item.quantity
                        product.save()
                order.status = 'ordered'
                order.save()
                send_email_order_placed.delay(self.request.user.id, order.id)
                messages.success(request, 'Order was placed successfully!')
                return redirect('backend:cart')
            except Order.DoesNotExist:
                messages.error(request, 'Order does not found! Please try '
                                        'again!')
                return redirect('backend:cart')


@login_required
def add_to_cart(request, product_id, quantity=1):
    product = get_object_or_404(Product,
                                pk=product_id)
    product_info = get_object_or_404(ProductInfo,
                                     product=product)

    if quantity <= int(product_info.quantity):
        order, created = Order.objects.get_or_create(status='new',
                                                     is_active=True,
                                                     user=request.user,
                                                     contact=request.user.contacts.
                                                     first())
        order_item, created = OrderItem.objects.get_or_create(
            brand=product_info.brand,
            category=product_info.category,
            product=product,
            order=order,
            shop=product_info.shop)
        order_item.quantity += quantity
        order_item.save()
        messages.success(request, 'Product added to cart successfully!')
        return redirect(request.META.get('HTTP_REFERER',
                                         'redirect_if_referer_not_found'))
    else:
        messages.error(request, 'SORRY, OUT OF STOCK OR TO MANY!')
        return redirect(request.META.get('HTTP_REFERER',
                                         'redirect_if_referer_not_found'))


@login_required
def remove_from_cart(request, item_id):
    try:
        order = Order.objects.filter(status='new',
                                     is_active=True).get(user=request.user)
        try:
            order_item = OrderItem.objects.filter(order=order).get(id=item_id)
            product = ProductInfo.objects.get(product=order_item.product)
            product.quantity += order_item.quantity
            order_item.delete()
            product.save()
            return redirect('authorization:cart')
        except OrderItem.DoesNotExist:
            messages.error(request, 'Something WRONG!')
            return redirect('authorization:cart')
    except Order.DoesNotExist:
        messages.error(request, 'Something WRONG!')
        return redirect('authorization:cart')

def search(request):
    if request.method == 'GET':
        search_query = request.GET.get('search')
        if search_query:
            results = Product.objects.filter(Q(name__icontains=search_query) | Q(
                description__icontains=search_query))
            data = {
                'results': results,
                'search_query': search_query
            }
            return render(request, 'search.html', data)
        else:
            messages.error(request, 'Please enter a search query!')
            return render(request, 'search.html')