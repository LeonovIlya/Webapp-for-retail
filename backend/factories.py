import factory
import factory.fuzzy
import random

from backend.models import Brand, Category, Parameter, Product, ProductInfo, \
    ProductParameter, Shop


class BrandFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Brand

    name = factory.Faker('company')


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Faker('language_name')

    @factory.post_generation
    def shops(self, create, *kwargs):
        if create:
            shop_list = tuple(Shop.objects.all().values_list('id',
                                                             flat=True))
            shop_list_rnd = random.sample(shop_list,
                                          random.randint(1, len(shop_list)))
            for shop in shop_list_rnd:
                self.shops.add(shop)


@factory.django.mute_signals()
class ShopFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Shop
        django_get_or_create = ('user',)

    name = factory.Faker('company')
    url = factory.Faker('url')
    user = factory.SubFactory('authorization.factories.UserFactory',
                              shop=None,
                              type='shop')


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Faker('catch_phrase')
    category = factory.fuzzy.FuzzyChoice(Category.objects.all())


class ProductInfoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductInfo

    model = factory.Faker('nic_handle')
    brand = factory.fuzzy.FuzzyChoice(Brand.objects.all())
    quantity = factory.Faker('random_digit_not_null')
    price = factory.Faker('port_number')
    price_rrc = factory.Faker('port_number')
    product = factory.SubFactory(ProductFactory)
    shop = factory.fuzzy.FuzzyChoice(Shop.objects.all())


class ParameterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Parameter

    name = factory.Faker('uri_page')


class ProductParameterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductParameter

    product_info = factory.SubFactory(ProductInfoFactory)
    parameter = factory.Iterator(ParameterFactory)
    value = factory.Faker('ean8')
