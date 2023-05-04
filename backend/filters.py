import django_filters
from .models import ProductInfo


class ProductPriceFilter(django_filters.FilterSet):
    price = django_filters.AllValuesFilter()

    class Meta:
        model = ProductInfo
        fields = ['price']
