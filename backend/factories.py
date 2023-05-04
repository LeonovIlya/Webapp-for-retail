import os
import factory
import factory.fuzzy
import openai
import random
import requests
import shutil
import time

from io import BytesIO
from PIL import Image

import config
from backend.models import Brand, Category, Parameter, Product, ProductInfo, \
    ProductParameter, Shop

from shop.settings import BASE_DIR, MEDIA_ROOT
from backend.test import generate_pic


openai.api_key = config.AI_API_TOKEN


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


def generate_products_pics():
    product_names = list(Product.objects.all().values_list('name',
                                                           flat=True))
    for name in product_names:
        try:
            time.sleep(5)
            response = openai.Image.create(
                prompt=name,
                n=1,
                size="512x512"
            )
            pic_url = (response['data'][0]['url'])
            res = requests.get(pic_url, stream=True)
            if res.status_code == 200:
                with open(f'{MEDIA_ROOT}/products/{name}.png', 'wb') as f:
                    shutil.copyfileobj(res.raw, f)
                print('Image sucessfully Downloaded: ', name)
                Product.objects.filter(name=name).update(
                    image=f'products/{name}.png')
            else:
                print('Image Couldn\'t be retrieved')

        except openai.error.OpenAIError as e:
            print(e.http_status)
            print(e.error)


