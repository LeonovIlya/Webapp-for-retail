from django.db import models
from django.db.models import Avg
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from django.core.files.storage import FileSystemStorage

storage = FileSystemStorage(location=settings.STORAGE)

STATUS_CHOICES = (
    ('new', 'Новый'),
    ('ordered', 'Заказан'),
    ('confirmed', 'Подтвержден'),
    ('assembled', 'Собран'),
    ('sent', 'Отправлен'),
    ('delivered', 'Доставлен'),
    ('canceled', 'Отменен'),
)


class Brand(models.Model):
    name = models.CharField('Торговая марка',
                            max_length=80)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Торговая марка'
        verbose_name_plural = 'Торговые марки'
        ordering = ('name',)


class Shop(models.Model):
    name = models.CharField(max_length=50,
                            verbose_name='Название')
    url = models.URLField(verbose_name='Ссылка',
                          null=True,
                          blank=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                verbose_name='Пользователь',
                                related_name='shop',
                                blank=True,
                                null=True,
                                on_delete=models.CASCADE)
    state = models.BooleanField(verbose_name='Статус получения заказов',
                                default=True)

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = "Список магазинов"
        ordering = ('name',)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=50,
                            verbose_name='Название категории')
    shops = models.ManyToManyField(Shop,
                                   verbose_name='Магазины',
                                   related_name='categories',
                                   blank=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Список категорий'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Parameter(models.Model):
    name = models.CharField(max_length=50,
                            verbose_name='Название параметра')

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = "Список параметров"
        ordering = ('name',)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100,
                            verbose_name='Название товара')
    image = models.ImageField(upload_to='products/',
                              null=True,
                              blank=True)
    parameters = models.ManyToManyField(Parameter,
                                        through="ProductsParameters",
                                        verbose_name='Параметр',
                                        related_name='parameters',
                                        blank=True)
    description = models.TextField(verbose_name='Описание',
                                   blank=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = "Список товаров"
        ordering = ('name',)

    def __str__(self):
        return self.name

    @property
    def average_rating(self):
        return self.comments.all().aggregate(Avg('rating'))['rating__avg']

    @property
    def count_rating_five(self):
        return self.comments.filter(rating=5).count()

    @property
    def count_rating_four(self):
        return self.comments.filter(rating=4).count()

    @property
    def count_rating_three(self):
        return self.comments.filter(rating=3).count()

    @property
    def count_rating_two(self):
        return self.comments.filter(rating=2).count()

    @property
    def count_rating_one(self):
        return self.comments.filter(rating=1).count()


class ProductsParameters(models.Model):
    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE)
    parameter = models.ForeignKey(Parameter,
                                  on_delete=models.CASCADE)
    value = models.CharField(max_length=100,
                             verbose_name='Значение')


class ProductInfo(models.Model):
    model = models.CharField(max_length=100,
                             verbose_name='Модель')
    brand = models.ForeignKey(Brand,
                              verbose_name='Торговая марка',
                              related_name='product_info',
                              blank=True,
                              on_delete=models.CASCADE)
    category = models.ForeignKey(Category,
                                 verbose_name='Категория',
                                 related_name='product_info',
                                 blank=True,
                                 on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    price = models.PositiveIntegerField(verbose_name='Цена')
    price_rrc = models.PositiveIntegerField(verbose_name='Рекомендуемая '
                                                         'розничная цена')
    product = models.ForeignKey(Product,
                                to_field='id',
                                verbose_name='Товар',
                                related_name='product_info',
                                blank=True,
                                on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop,
                             verbose_name='Магазин',
                             related_name='product_info',
                             blank=True,
                             on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Информация о товаре'
        verbose_name_plural = 'Список информации о товарах'
        constraints = [
            models.UniqueConstraint(fields=['product', 'shop'],
                                    name='unique_product_info'),
        ]
        ordering = ('product', 'price', 'quantity')

    def __str__(self):
        return f'{self.product.name} ({self.shop.name})'


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             verbose_name='Пользователь',
                             related_name='orders',
                             blank=True,
                             on_delete=models.CASCADE)
    contact = models.ForeignKey(settings.AUTH_CONTACT_MODEL,
                                verbose_name='Контакт',
                                related_name='Контакт',
                                blank=True,
                                null=True,
                                on_delete=models.CASCADE)
    status = models.CharField(max_length=15,
                              verbose_name='Статус',
                              choices=STATUS_CHOICES)
    total_items_count = models.IntegerField(verbose_name='Общее количество '
                                                         'товаров в заказе',
                                            default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = "Список заказов"
        ordering = ('-created',)

    def __str__(self):
        return f'{str(self.created)} : {self.user} : {self.status}' \
               f' {self.is_active}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order,
                              verbose_name='Заказ',
                              related_name='ordered_items',
                              blank=True,
                              on_delete=models.CASCADE)
    category = models.ForeignKey(Category,
                                 verbose_name='Категория товара',
                                 blank=True,
                                 null=True,
                                 on_delete=models.SET_NULL)
    shop = models.ForeignKey(Shop,
                             verbose_name='Магазин',
                             blank=True,
                             null=True,
                             on_delete=models.SET_NULL)
    brand = models.ForeignKey(Brand,
                              verbose_name='Торговая марка',
                              related_name='itemsInOrder',
                              on_delete=models.CASCADE,
                              blank=True)
    product = models.ForeignKey(Product,
                                verbose_name='Товар',
                                blank=True,
                                null=True,
                                on_delete=models.SET_NULL)
    quantity = models.PositiveIntegerField(default=0,
                                           verbose_name='Количество')
    price_per_item = models.DecimalField(default=0,
                                         max_digits=10,
                                         decimal_places=2,
                                         verbose_name='Цена за единицу')
    total_price = models.DecimalField(default=0,
                                      max_digits=10,
                                      decimal_places=2,
                                      verbose_name='Общая стоимость')

    class Meta:
        verbose_name = 'Товар в заказе'
        verbose_name_plural = "Товары в заказе"

    def __str__(self):
        return str(self.product)

    def save(self, *args, **kwargs):
        product = ProductInfo.objects.get(product=self.product)

        price_per_item = product.price
        self.price_per_item = price_per_item
        self.total_price = price_per_item * self.quantity

        super(OrderItem, self).save(*args, **kwargs)


@receiver(post_save, sender=OrderItem)
def item_in_order_post_save(sender, instance, created, **kwargs):
    all_items_in_order = OrderItem.objects.filter(order=instance.order)
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
    all_items_in_order = OrderItem.objects.filter(order=instance.order)
    order_total_price = 0
    total_items_count_in_order = 0
    for item in all_items_in_order:
        order_total_price += item.total_price
        total_items_count_in_order += item.quantity
    instance.order.total_price = order_total_price
    instance.order.total_items_count = total_items_count_in_order
    instance.order.save(force_update=True)
