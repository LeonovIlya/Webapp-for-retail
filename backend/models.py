from django.db import models
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from authorization.models import User, Contact

storage = FileSystemStorage(location=settings.STORAGE)

STATUS_CHOICES = (
    ('basket', 'Статус корзины'),
    ('new', 'Новый'),
    ('confirmed', 'Подтвержден'),
    ('assembled', 'Собран'),
    ('sent', 'Отправлен'),
    ('delivered', 'Доставлен'),
    ('canceled', 'Отменен'),
)


class Shop(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')
    url = models.URLField(verbose_name='Ссылка', null=True, blank=True)
    user = models.OneToOneField(User, verbose_name='Пользователь', related_name='shop',
                                blank=True, null=True,
                                on_delete=models.CASCADE)
    state = models.BooleanField(verbose_name='статус получения заказов', default=True)

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = "Список магазинов"
        ordering = ('-name',)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название категории')
    shops = models.ManyToManyField(Shop, verbose_name='Магазины', related_name='categories', blank=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Список категорий'
        ordering = ('-name',)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название продукта')
    category = models.ForeignKey(Category, verbose_name='Категория', related_name='products', blank=True,
                                 on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = "Список продуктов"
        ordering = ('-name',)

    def __str__(self):
        return f'{self.category} - {self.name}'


class ProductInfo(models.Model):
    model = models.CharField(max_length=100, verbose_name='Модель')
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    price = models.PositiveIntegerField(verbose_name='Цена')
    price_rrc = models.PositiveIntegerField(verbose_name='Рекомендуемая розничная цена')
    product = models.ForeignKey(Product, verbose_name='Продукт', related_name='product_infos', blank=True,
                                on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, verbose_name='Магазин', related_name='product_infos', blank=True,
                             on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Информация о продукте'
        verbose_name_plural = 'Информационный список о продуктах'
        constraints = [
            models.UniqueConstraint(fields=['product', 'shop'], name='unique_product_info'),
        ]

    def __str__(self):
        return f'{self.shop.name} - {self.product.name}'


class Brand(models.Model):
    name = models.CharField('Торговая марка', max_length=80)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Торговая марка'
        verbose_name_plural = 'Торговые марки'


class Parameter(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название параметра')

    class Meta:
        verbose_name = 'Название параметра'
        verbose_name_plural = "Список названий параметров"
        ordering = ('-name',)

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    product_info = models.ForeignKey(ProductInfo, verbose_name='Информация о продукте', blank=True,
                                     related_name='product_parameters', on_delete=models.CASCADE)
    parameter = models.ForeignKey(Parameter, verbose_name='Параметр', related_name='product_parameters', blank=True,
                                  on_delete=models.CASCADE)
    value = models.CharField(max_length=100, verbose_name='Значение')

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = 'Список параметров'
        constraints = [
            models.UniqueConstraint(fields=['product_info', 'parameter'], name='unique_product_parameter'),
        ]

    def __str__(self):
        return f'{self.product_info.model} - {self.parameter.name}'


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Пользователь', related_name='orders', blank=True,
                             on_delete=models.CASCADE)
    contact = models.ForeignKey(settings.AUTH_CONTACT_MODEL, verbose_name='Контакт', related_name='Контакт', blank=True, null=True,
                                on_delete=models.CASCADE)
    status = models.CharField(max_length=15, verbose_name='Статус', choices=STATUS_CHOICES)
    total_items_count = models.IntegerField(verbose_name='Общее количество товаров в заказе', default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = "Список заказов"
        ordering = ('-created',)

    def __str__(self):
        return f'{str(self.created)} : {self.user} : {self.status} {self.is_active}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name='Заказ', related_name='ordered_items', blank=True,
                              on_delete=models.CASCADE)
    category = models.ForeignKey(Category, verbose_name='Категория товара', blank=True, null=True,
                                 on_delete=models.SET_NULL)
    shop = models.ForeignKey(Shop, verbose_name='магазин', blank=True, null=True, on_delete=models.SET_NULL)
    product_name = models.ForeignKey(Brand, verbose_name='Торговая марка', related_name='itemsInOrder',
                                     on_delete=models.CASCADE, blank=True)
    model = models.CharField('Модель', max_length=80)
    external_id = models.PositiveIntegerField(verbose_name='Внешний ИД', blank=True)
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')
    price_per_item = models.DecimalField(default=0, max_digits=10, decimal_places=2, verbose_name='Цена за единицу')
    total_price = models.DecimalField(default=0, max_digits=10, decimal_places=2, verbose_name='Общая стоимость')

    class Meta:
        verbose_name = 'Товар в заказе'
        verbose_name_plural = "Товары в заказе"

    def __str__(self):
        return str(self.product_name)

    def save(self, *args, **kwargs):
        product = Product.objects.get(name=self.product_name, shop=self.shop, model=self.model)

        price_per_item = product.price
        self.price_per_item = price_per_item
        self.total_price = price_per_item * self.quantity

        super(ItemInOrder, self).save(*args, **kwargs)


@receiver(post_save, sender=OrderItem)
def item_in_order_post_save(sender, instance, created, **kwargs):
    all_items_in_order = ItemInOrder.objects.filter(order=instance.order)
    order_total_price = 0
    total_items_count_in_order = 0
    for item in all_items_in_order:
        order_total_price += item.total_price
        total_items_count_in_order += item.quantity
    instance.order.total_price = order_total_price
    instance.order.total_items_count = total_items_count_in_order
    instance.order.save(force_update=True)


@receiver(post_delete, sender=OrderItem)
def item_in_order_post_delete(sender, instance, created=False, **kwargs):
    all_items_in_order = ItemInOrder.objects.filter(order=instance.order)
    order_total_price = 0
    total_items_count_in_order = 0
    for item in all_items_in_order:
        order_total_price += item.total_price
        total_items_count_in_order += item.quantity
    instance.order.total_price = order_total_price
    instance.order.total_items_count = total_items_count_in_order
    instance.order.save(force_update=True)