from rest_framework import serializers
from authorization.models import User, Contact
from .models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Order, OrderItem


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('id', 'city', 'street', 'house', 'apartment', 'e_mail', 'user', 'phone', 'work_phone',)
        read_only_fields = ('id',)
        extra_kwargs = {
            'user': {'write_only': True}
        }


class UserSerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'company', 'position', 'type', 'contacts')
        read_only_fields = ('id',)


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ('id', 'name', 'state')
        read_only_fields = ('id',)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name',)
        read_only_fields = ('id',)


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = ('name', 'category',)


class ProductParameterSerializer(serializers.ModelSerializer):
    parameter = serializers.StringRelatedField()

    class Meta:
        model = ProductParameter
        fields = ('parameter', 'value',)


class ProductInfoSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_parameters = ProductParameterSerializer(read_only=True, many=True)

    class Meta:
        model = ProductInfo
        fields = ('id', 'model', 'product', 'shop', 'quantity', 'price', 'price_rrc', 'product_parameters',)
        read_only_fields = ('id',)


class OrderItemSerializer(serializers.ModelSerializer):
    shop = serializers.StringRelatedField()
    category = serializers.StringRelatedField()
    product_name = serializers.StringRelatedField()

    class Meta:
        model = OrderItem
        fields = ['id', 'external_id', 'category', 'shop', 'product_name', 'model', 'quantity',
                  'price_per_item', 'total_price']
        read_only_fields = ['id', 'price_per_item', 'total_price']


class OrderItemAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['external_id', 'category', 'shop', 'product_name', 'model', 'quantity', 'order']


class OrderCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    contact = ContactSerializer

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['status', 'contact', 'total_price', 'total_items_count']


class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'status', 'contact']
        read_only_fields = ['id']


class OrderSerializer(serializers.ModelSerializer):
    ordered_items = OrderItemSerializer(read_only=True, many=True)
    total_price = serializers.IntegerField()
    total_items_count = serializers.IntegerField()
    contact = ContactSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'status', 'total_items_count',
                  'total_price', 'contact', 'ordered_items')
        read_only_fields = ('id',)
