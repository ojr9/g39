from mangopay.fields import MoneyField, AddressField
from mangopay.utils import Money, Address
from django.db.models.fields import Field


class MangoMoneyField(Money, Field):
    pass


class MangoAddressField(AddressField, Field):
    pass



