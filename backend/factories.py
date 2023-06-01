import os
import factory
import factory.fuzzy
import openai
import random
import requests
import shutil
import time

from faker import Faker
from io import BytesIO
from PIL import Image

import config
from backend.models import Brand, Category, Parameter, Product, ProductInfo,\
    ProductsParameters, Shop

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

    name = factory.Faker('cryptocurrency_name')

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


class ParameterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Parameter

    name = factory.Faker('cryptocurrency_code')


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Faker('catch_phrase')

    @factory.post_generation
    def parameters(self, create, *kwargs):
        if create:
            par_list = tuple(Parameter.objects.all().values_list('id',
                                                                 flat=True))
            for par in par_list:
                self.parameters.add(par)


class ProductInfoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductInfo

    model = factory.Faker('nic_handle')
    brand = factory.fuzzy.FuzzyChoice(Brand.objects.all())
    category = factory.fuzzy.FuzzyChoice(Category.objects.all())
    quantity = factory.Faker('pyint')
    price = factory.Faker('port_number')
    price_rrc = factory.Faker('port_number')
    product = factory.SubFactory(ProductFactory)
    shop = factory.fuzzy.FuzzyChoice(Shop.objects.all())


# class ProductsParametersFactory(factory.django.DjangoModelFactory):
#     class Meta:
#         model = ProductsParameters
#
#     product = factory.SubFactory(ProductFactory)
#     parameter = factory.SubFactory(ParameterFactory)
#     value = factory.Faker('pyint')
#
#
# class ProductWithParametersFactory(ProductFactory):
#     reports = factory.RelatedFactory(
#         ProductsParametersFactory,
#         factory_related_name='product')


def generate_products_pics():
    product_names = list(Product.objects.all().values_list('name',
                                                           flat=True))
    for name in product_names:
        try:
            if Product.objects.values('image').filter(name=name)[0]['image']:
                print('Link to image already exist: ', name)
            else:
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
                    Product.objects.filter(name=name).update(
                        image=f'products/{name}.png')
                    print('Image successfully downloaded: ', name)
                else:
                    print('Image Couldn\'t be retrieved')

        except openai.error.OpenAIError as e:
            print(e.http_status)
            print(e.error)


def generate_products_descriptions():
    product_names = list(Product.objects.all().values_list('name',
                                                           flat=True))
    for name in product_names:
        try:
            if Product.objects.values('description').filter(
                    name=name)[0]['description']:
                print('Description already exist: ', name)
            else:
                time.sleep(5)
                res = openai.Completion.create(
                    model='text-davinci-003',
                    prompt=f'Write a creative ad for the following product '
                           f'with name {name}',
                    temperature=0.5,
                    max_tokens=100,
                    top_p=1.0,
                    frequency_penalty=0.0,
                    presence_penalty=0.0
                )

                Product.objects.filter(name=name).update(
                    description=res['choices'][0]['text'])
                print('Description successfully added: ', name)
        except openai.error.OpenAIError as e:
            print(e.http_status)
            print(e.error)


def set_param_values():
    id_list = list(ProductsParameters.objects.all().values_list('id',
                                                                flat=True))
    for _id in id_list:
        fake = Faker()
        ProductsParameters.objects.filter(id=_id).update(value=fake.pyint())
