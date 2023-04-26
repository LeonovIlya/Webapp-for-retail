from django.contrib import admin

from .models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Order, OrderItem, Brand

# admin.site.register(Shop)
# admin.site.register(Category)
# admin.site.register(Product)
# admin.site.register(Parameter)
# admin.site.register(ProductParameter)
# admin.site.register(Order)
# admin.site.register(OrderItem)


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'url', 'user']
    list_display_links = ['id', 'name', 'url', 'user']


@admin.register(Category)
class ShopAdmin(admin.ModelAdmin):
    pass


@admin.register(Product)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    list_filter = ['name']


@admin.register(ProductInfo)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['product', 'model', 'shop', 'quantity', 'price', 'price_rrc']
    list_filter = ['product']


@admin.register(Parameter)
class ShopAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductParameter)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['product_info', 'parameter', 'value']
    list_filter = ['product_info', 'parameter']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'created', 'updated',
                    'total_items_count']
    list_display_links = ['user']
    list_filter = ['user', 'status', 'created', 'updated', ]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'category', 'shop', 'product_name', 'model',
                    'quantity', 'price_per_item', 'total_price']


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name']