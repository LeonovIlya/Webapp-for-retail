import factory
from backend.models import Brand, Category, Shop


class BrandFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Brand

    name = factory.Faker('company')


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Faker('language_name')

    @factory.post_generation
    def shops(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for shop in extracted:
                self.shops.add(shop)


@factory.django.mute_signals()
class ShopFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Shop
        django_get_or_create = ('user',)

    name = factory.Faker('company')
    url = factory.Faker('url')
    user = factory.SubFactory('authorization.factories.UserFactory',
                              shop=None)
