from django import forms

from .models import MangoPayOut, MangoBankAccount


supported_currencies = (('EUR','Euro'), ('USD', 'US Dollar'), ('CHF', 'Swiss Franc'))


class MangoPayoutForm(forms.ModelForm):
    class Meta:
        model = MangoPayOut
        fields = ['bank_wire_ref', 'amount']


class MangoBankAccountForm(forms.ModelForm):
    class Meta:
        model = MangoBankAccount
        fields = ['account_number', 'currency', 'description', 'al1', 'al2', 'city', 'pc', 'country']
        widgets = {'currency': forms.Select(choices=supported_currencies)}


class TopUpStartForm(forms.Form):
    amount = forms.DecimalField(max_digits=8, decimal_places=2)
    description = forms.CharField(min_length=15, max_length=50)
    payment_method = forms.ChoiceField(choices=(('Card', 'Top up via card'), ('BW', 'Top up via Bankwire')))
