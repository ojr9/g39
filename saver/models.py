from django.db import models
from django.contrib.auth.models import User
# from django.urls import reverse

from mangopay.utils import Address
from payment.fields import MangoAddressField
USER_TYPES = (('NAT', 'Natural'), ('LEG', 'Legal'))


def _make_address(**kwargs):
    return Address(address_line_1=kwargs['line1'], address_line_2=kwargs['line2'], region=kwargs['region'],
                   postal_code=kwargs['pc'], country=kwargs['country'])


class Saver(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name='user_saver')
    created = models.DateTimeField(auto_now_add=True)
    mid = models.PositiveIntegerField(default=0)
    user_type = models.CharField(max_length=3, choices=USER_TYPES)
    active = models.BooleanField(default=True)
    validated = models.BooleanField(default=False)
    birthday = models.DateField(blank=True, null=True)
    nationality = models.CharField(max_length=100, default='DE') # need to change these fields to country fields
    country_of_residence = models.CharField(max_length=100, default='DE') # same
    # address = MangoAddressField(name)
    # address = models.JSONField(default=None) see comment below

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'{self.mid} : {self.user} : {self.user_type}'

    def deactivate(self):
        self.active = False
        self.save()

    # def get_absolute_url(self):
    #     return reverse('saverview', kwargs={'id': self.id})

    # There are a few issues with the address field from the SDK, it is not passed intothe ORM and database is not
    # updated, meaning the table is not updated with this. Either I make a custom field, or get a package with fields
    # made or I use a JSONField. This should work in that it would simply save a dict. To see later.
    # def make_address(self, line1, line2, region, pc, coutry):
    #     self.address = _make_address(line1, line2, region, pc, country)
    #     self.save()


class CorpSaver(models.Model):
    # Will get this here when there is a 
    pass