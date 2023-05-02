import factory
from authorization.models import User, Contact
from backend.factories import ShopFactory


@factory.django.mute_signals()
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Faker('email')
    company = factory.Faker('company')
    position = factory.Faker('job')
    username = factory.Faker('user_name')
    password = factory.Faker('password')


class ContactFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Contact

    city = factory.Faker('city')
    street = factory.Faker('street_name')
    house = factory.Faker('building_number')
    phone = factory.Faker('phone_number')
    user = factory.SubFactory(UserFactory)
