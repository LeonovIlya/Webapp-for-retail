from django.contrib import admin

from .models import Shop, Category, Product, ProductInfo, Parameter, Order, \
    OrderItem, Brand


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'url', 'user']
    list_filter = ['name']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'image']


@admin.register(ProductInfo)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['id', 'brand', 'category', 'product', 'model', 'shop',
                    'quantity', 'price', 'price_rrc']
    list_filter = ['brand', 'category', 'shop']


@admin.register(Parameter)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'created', 'updated',
                    'total_items_count']
    list_display_links = ['user']
    list_filter = ['user', 'status', 'created', 'updated']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'category', 'shop', 'brand', 'product',
                    'quantity', 'price_per_item', 'total_price']


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
