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

from .tasks import import_shop_data
from .signals import new_user_registered
from .models import Category, Shop, ProductInfo, Order, OrderItem, Product, \
    Parameter, Brand
from authorization.forms import CommentForm
from authorization.models import Contact, ConfirmEmailToken, Comment, User
from authorization.serializers import CommentSerializer
from .serializers import CategorySerializer, ShopSerializer, \
    ProductInfoSerializer, OrderSerializer, OrderItemSerializer, \
    UserSerializer, ContactSerializer, ProductSerializer


# class RegisterAccount(APIView):
#     throttle_scope = 'anon'
#
#     @staticmethod
#     def post(request, *args, **kwargs):
#         if {'first_name', 'last_name', 'email', 'password', 'company',
#             'position'}.issubset(request.data):
#             errors = {}
#             try:
#                 validate_password(request.data['password'])
#             except Exception as password_error:
#                 error_array = []
#                 for item in password_error:
#                     error_array.append(item)
#                 return JsonResponse(
#                     {'Status': False, 'Errors': {'password': error_array}})
#             else:
#                 request.data.update({})
#                 user_serializer = UserSerializer(data=request.data)
#                 if user_serializer.is_valid():
#                     user = user_serializer.save()
#                     user.set_password(request.data['password'])
#                     user.save()
#                     return JsonResponse({'Status': True})
#                 else:
#                     return JsonResponse(
#                         {'Status': False, 'Errors': user_serializer.errors})
#
#         return JsonResponse({'Status': False,
#                              'Errors': 'Не указаны все необходимые аргументы'})
#
#
# class ConfirmAccount(APIView):
#     throttle_scope = 'anon'
#
#     @staticmethod
#     def post(request, *args, **kwargs):
#         if {'email', 'token'}.issubset(request.data):
#
#             token = ConfirmEmailToken.objects.filter(
#                 user__email=request.data['email'],
#                 key=request.data['token']).first()
#             if token:
#                 token.user.is_active = True
#                 token.user.save()
#                 token.delete()
#                 return Response({'Status': True})
#             else:
#                 return Response({'Status': False,
#                                  'Errors': 'Неправильно указан токен или email'})
#         return Response({'Status': False,
#                          'Errors': 'Не указаны все необходимые аргументы'},
#                         status=status.HTTP_400_BAD_REQUEST)
#
#
# class LoginAccount(APIView):
#     throttle_scope = 'anon'
#
#     @staticmethod
#     def post(request, *args, **kwargs):
#         if {'email', 'password'}.issubset(request.data):
#             user = authenticate(request, username=request.data['email'],
#                                 password=request.data['password'])
#             if user is not None:
#                 if user.is_active:
#                     token, _ = Token.objects.get_or_create(user=user)
#
#                     return Response({'Status': True, 'Token': token.key})
#
#             return Response(
#                 {'Status': False, 'Errors': 'Не удалось авторизовать'},
#                 status=status.HTTP_403_FORBIDDEN)
#         return Response({'Status': False,
#                          'Errors': 'Не указаны все необходимые аргументы'},
#                         status=status.HTTP_400_BAD_REQUEST)
#
#
# class AccountDetails(APIView):
#     throttle_scope = 'user'
#
#     @staticmethod
#     def get(request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return Response({'Status': False, 'Error': 'Login required'},
#                             status=status.HTTP_403_FORBIDDEN)
#         serializer = UserSerializer(request.user)
#         return Response(serializer.data)
#
#     @staticmethod
#     def post(request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return Response({'Status': False, 'Error': 'Login required'},
#                             status=status.HTTP_403_FORBIDDEN)
#         if 'password' in request.data:
#             try:
#                 validate_password(request.data['password'])
#             except Exception as password_error:
#                 return Response(
#                     {'Status': False, 'Errors': {'password': password_error}})
#             else:
#                 request.user.set_password(request.data['password'])
#         user_serializer = UserSerializer(request.user, data=request.data,
#                                          partial=True)
#         if user_serializer.is_valid():
#             user_serializer.save()
#             return Response({'Status': True}, status=status.HTTP_201_CREATED)
#         else:
#             return Response(
#                 {'Status': False, 'Errors': user_serializer.errors},
#                 status=status.HTTP_400_BAD_REQUEST)
#
#
# class CategoryView(viewsets.ModelViewSet):
#     queryset = Category.objects.all()
#     serializer_class = CategorySerializer
#     ordering = ('name',)
#
#
# class ShopView(viewsets.ModelViewSet):
#     queryset = Shop.objects.all()
#     serializer_class = ShopSerializer
#     ordering = ('name',)
#
#
# class ProductsInfoView(viewsets.ReadOnlyModelViewSet):
#     throttle_scope = 'anon'
#     serializer_class = ProductInfoSerializer
#     ordering = ('product',)
#
#     def get_queryset(self):
#         query = Q(shop__state=True)
#         shop_id = self.request.query_params.get('shop_id')
#         category_id = self.request.query_params.get('category_id')
#         if shop_id:
#             query = query & Q(shop_id=shop_id)
#         if category_id:
#             query = query & Q(product__category_id=category_id)
#         queryset = ProductInfo.objects.filter(
#             query).select_related(
#             'shop', 'product__category').prefetch_related(
#             'product_parameters__parameter').distinct()
#         return queryset
#
#
# class BasketView(APIView):
#     throttle_scope = 'user'
#
#     @staticmethod
#     def get(request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return JsonResponse({'Status': False, 'Error': 'Log in required'},
#                                 status=status.HTTP_403_FORBIDDEN)
#         basket = Order.objects.filter(
#             user_id=request.user.id, status='basket').prefetch_related(
#             'ordered_items__product_info__product__category',
#             'ordered_items__product_info__product_parameters__parameter').annotate(
#             total_sum=Sum(F('ordered_items__quantity') * F(
#                 'ordered_items__product_info__price'))).distinct()
#         serializer = OrderSerializer(basket, many=True)
#         return Response(serializer.data)
#
#     @staticmethod
#     def post(request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return JsonResponse({'Status': False, 'Error': 'Log in required'},
#                                 status=status.HTTP_403_FORBIDDEN)
#         items_sting = request.data.get('items')
#         if items_sting:
#             try:
#                 items_dict = load_json(items_sting)
#             except ValueError:
#                 JsonResponse(
#                     {'Status': False, 'Errors': 'Неверный формат запроса'})
#             else:
#                 basket, _ = Order.objects.get_or_create(
#                     user_id=request.user.id,
#                     state='basket')
#                 objects_created = 0
#                 for order_item in items_dict:
#                     order_item.update({'order': basket.id})
#                     serializer = OrderItemSerializer(data=order_item)
#                     if serializer.is_valid():
#                         try:
#                             serializer.save()
#                         except IntegrityError as error:
#                             return JsonResponse(
#                                 {'Status': False, 'Errors': str(error)})
#                         else:
#                             objects_created += 1
#                     else:
#                         JsonResponse(
#                             {'Status': False, 'Errors': serializer.errors})
#                 return JsonResponse(
#                     {'Status': True, 'Создано объектов': objects_created})
#         return JsonResponse({'Status': False,
#                              'Errors': 'Не указаны все необходимые аргументы'})
#
#     @staticmethod
#     def delete(request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return JsonResponse({'Status': False, 'Error': 'Log in required'},
#                                 status=status.HTTP_403_FORBIDDEN)
#         items_sting = request.data.get('items')
#         if items_sting:
#             items_list = items_sting.split(',')
#             basket, _ = Order.objects.get_or_create(user_id=request.user.id,
#                                                     state='basket')
#             query = Q()
#             objects_deleted = False
#             for order_item_id in items_list:
#                 if order_item_id.isdigit():
#                     query = query | Q(order_id=basket.id,
#                                       id=order_item_id)
#                     objects_deleted = True
#             if objects_deleted:
#                 deleted_count = OrderItem.objects.filter(query).delete()[0]
#                 return JsonResponse(
#                     {'Status': True, 'Удалено объектов': deleted_count})
#         return JsonResponse({'Status': False,
#                              'Errors': 'Не указаны все необходимые аргументы'})
#
#     @staticmethod
#     def put(request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return JsonResponse({'Status': False, 'Error': 'Log in required'},
#                                 status=status.HTTP_403_FORBIDDEN)
#
#         items_sting = request.data.get('items')
#         if items_sting:
#             try:
#                 items_dict = load_json(items_sting)
#             except ValueError:
#                 JsonResponse(
#                     {'Status': False, 'Errors': 'Неверный формат запроса'})
#             else:
#                 basket, _ = Order.objects.get_or_create(
#                     user_id=request.user.id,
#                     state='basket')
#                 objects_updated = 0
#                 for order_item in items_dict:
#                     if type(order_item['id']) == int and type(
#                             order_item['quantity']) == int:
#                         objects_updated += OrderItem.objects.filter(
#                             order_id=basket.id,
#                             id=order_item['id']).update(
#                             quantity=order_item['quantity'])
#                 return JsonResponse(
#                     {'Status': True, 'Обновлено объектов': objects_updated})
#         return JsonResponse({'Status': False,
#                              'Errors': 'Не указаны все необходимые аргументы'})
#
#
# class OrderView(APIView):
#     throttle_scope = 'user'
#
#     @staticmethod
#     def get(request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return Response({'Status': False, 'Error': 'Log in required'},
#                             status=status.HTTP_403_FORBIDDEN)
#
#         order = Order.objects.filter(
#             user_id=request.user.id).exclude(status='basket').select_related(
#             'contact').prefetch_related(
#             'ordered_items').annotate(
#             total_quantity=Sum('ordered_items__quantity'),
#             total_sum=Sum('ordered_items__total_amount')).distinct()
#
#         serializer = OrderSerializer(order, many=True)
#         return Response(serializer.data)
#
#     @staticmethod
#     def post(request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return Response({'Status': False, 'Error': 'Log in required'},
#                             status=status.HTTP_403_FORBIDDEN)
#
#         if request.data['id'].isdigit():
#             try:
#                 is_updated = Order.objects.filter(
#                     id=request.data['id'],
#                     user_id=request.user.id).update(
#                     contact_id=request.data['contact'],
#                     status='new')
#             except IntegrityError as error:
#                 return Response({'Status': False,
#                                  'Errors': 'Неправильно указаны аргументы'},
#                                 status=status.HTTP_400_BAD_REQUEST)
#             else:
#                 if is_updated:
#                     request.user.email_user(f'Обновление статуса заказа',
#                                             'Заказ сформирован',
#                                             from_email=settings.EMAIL_HOST_USER)
#                     return Response({'Status': True})
#         return Response({'Status': False,
#                          'Errors': 'Не указаны все необходимые аргументы'},
#                         status=status.HTTP_400_BAD_REQUEST)
#
#
# class ContactView(APIView):
#     throttle_scope = 'user'
#
#     @staticmethod
#     def get(request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return JsonResponse({'Status': False, 'Error': 'Log in required'},
#                                 status=status.HTTP_403_FORBIDDEN)
#         contact = Contact.objects.filter(
#             user_id=request.user.id)
#         serializer = ContactSerializer(contact, many=True)
#         return Response(serializer.data)
#
#     @staticmethod
#     def post(request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return JsonResponse({'Status': False, 'Error': 'Log in required'},
#                                 status=status.HTTP_403_FORBIDDEN)
#         if {'city', 'phone'}.issubset(request.data):
#             request.data._mutable = True
#             request.data.update({'user': request.user.id})
#             serializer = ContactSerializer(data=request.data)
#             if serializer.is_valid():
#                 serializer.save()
#                 return JsonResponse({'Status': True})
#             else:
#                 JsonResponse({'Status': False, 'Errors': serializer.errors})
#
#         return JsonResponse({'Status': False,
#                              'Errors': 'Не указаны все необходимые аргументы'})
#
#     @staticmethod
#     def delete(request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return JsonResponse({'Status': False, 'Error': 'Log in required'},
#                                 status=status.HTTP_403_FORBIDDEN)
#         items_sting = request.data.get('items')
#         if items_sting:
#             items_list = items_sting.split(',')
#             query = Q()
#             objects_deleted = False
#             for contact_id in items_list:
#                 if contact_id.isdigit():
#                     query = query | Q(user_id=request.user.id,
#                                       id=contact_id)
#                     objects_deleted = True
#             if objects_deleted:
#                 deleted_count = Contact.objects.filter(query).delete()[0]
#                 return JsonResponse(
#                     {'Status': True, 'Удалено объектов': deleted_count})
#         return JsonResponse({'Status': False,
#                              'Errors': 'Не указаны все необходимые аргументы'})
#
#     @staticmethod
#     def put(request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return JsonResponse({'Status': False, 'Error': 'Log in required'},
#                                 status=status.HTTP_403_FORBIDDEN)
#         if 'id' in request.data:
#             if request.data['id'].isdigit():
#                 contact = Contact.objects.filter(id=request.data['id'],
#                                                  user_id=request.user.id).first()
#                 print(contact)
#                 if contact:
#                     serializer = ContactSerializer(contact, data=request.data,
#                                                    partial=True)
#                     if serializer.is_valid():
#                         serializer.save()
#                         return JsonResponse({'Status': True})
#                     else:
#                         JsonResponse(
#                             {'Status': False, 'Errors': serializer.errors})
#         return JsonResponse({'Status': False,
#                              'Errors': 'Не указаны все необходимые аргументы'})
#
#
# class PartnerOrders(APIView):
#     throttle_scope = 'user'
#
#     @staticmethod
#     def get(request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return Response({'Status': False, 'Error': 'Login required'},
#                             status=status.HTTP_403_FORBIDDEN)
#         if request.user.type != 'shop':
#             return Response({'Status': False, 'Error': 'Только для магазинов'},
#                             status=status.HTTP_403_FORBIDDEN)
#         pr = Prefetch('ordered_items',
#                       queryset=OrderItem.objects.filter(
#                           shop__user_id=request.user.id))
#         order = Order.objects.filter(
#             ordered_items__shop__user_id=request.user.id).exclude(
#             status='basket') \
#             .prefetch_related(pr).select_related('contact').annotate(
#             total_sum=Sum('ordered_items__total_amount'),
#             total_quantity=Sum('ordered_items__quantity'))
#         serializer = OrderSerializer(order,
#                                      many=True)
#         return Response(serializer.data)
#
#
# class PartnerState(APIView):
#     throttle_scope = 'user'
#
#     @staticmethod
#     def get(request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return Response({'Status': False, 'Error': 'Login required'},
#                             status=status.HTTP_403_FORBIDDEN)
#         if request.user.type != 'shop':
#             return Response({'Status': False, 'Error': 'Только для магазинов'},
#                             status=status.HTTP_403_FORBIDDEN)
#         shop = request.user.shop
#         serializer = ShopSerializer(shop)
#         return Response(serializer.data)
#
#     @staticmethod
#     def post(request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return Response({'Status': False, 'Error': 'Log in required'},
#                             status=status.HTTP_403_FORBIDDEN)
#         if request.user.type != 'shop':
#             return Response({'Status': False, 'Error': 'Только для магазинов'},
#                             status=status.HTTP_403_FORBIDDEN)
#         state = request.data.get('state')
#         if state:
#             try:
#                 Shop.objects.filter(user_id=request.user.id).update(
#                     state=strtobool(state))
#                 return Response({'Status': True})
#             except ValueError as error:
#                 return Response({'Status': False, 'Errors': str(error)},
#                                 status=status.HTTP_400_BAD_REQUEST)
#         return Response(
#             {'Status': False, 'Errors': 'Не указан аргумент state.'},
#             status=status.HTTP_400_BAD_REQUEST)
#
#
# class PartnerUpdate(APIView):
#     throttle_scope = 'partner'
#
#     @staticmethod
#     def post(request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return Response({'Status': False, 'Error': 'Log in required'},
#                             status=status.HTTP_403_FORBIDDEN)
#         if request.user.type != 'shop':
#             return Response({'Status': False, 'Error': 'Только для магазинов'},
#                             status=status.HTTP_403_FORBIDDEN)
#         file = request.FILES
#         if file:
#             user_id = request.user.id
#             import_shop_data(file, user_id)
#             return Response({'Status': True})
#         return Response({'Status': False,
#                          'Errors': 'Не указаны все необходимые аргументы'},
#                         status=status.HTTP_400_BAD_REQUEST)


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