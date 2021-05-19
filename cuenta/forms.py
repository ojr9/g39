from django import forms

from payment.models import MangoCard
from saver.models import Saver
from .models import GoalSaving, Cuenta, GroupSave, LinkPayment


class GoalSaveCreateForm(forms.ModelForm):
    class Meta:
        model = GoalSaving
        fields = ['title', 'description', 'goal', 'monthly', 'duration', 'image', 'video']


class GroupSaveCreateForm(forms.ModelForm):
    class Meta:
        model = GroupSave
        fields = ['account', 'title', 'description', 'goal', 'image', 'video']

    def __init__(self, user, *args, **kwargs):
        super(GroupSaveCreateForm, self).__init__(*args, **kwargs)
        self.fields['account'].queryset = Cuenta.objects.filter(user=user)


class Deposit(forms.Form):
    amount = forms.IntegerField(max_value=2500, min_value=50)
    description = forms.CharField(max_length=150, min_length=3, required=False)
    card = forms.ModelChoiceField(queryset=None)

    def __init__(self, user, currency, *args, **kwargs):
        super(Deposit, self).__init__(*args, **kwargs)
        saver = Saver.objects.get(user=user)
        self.fields['card'].queryset = MangoCard.objects.filter(saver=saver, currency=currency)


class PaymentLinkCreateForm(forms.ModelForm):
    email = forms.EmailField(required=False, help_text='Add email of the payer in here if you want to send it right '
                                                       'away. Or leave blank to send it later.')

    class Meta:
        model = LinkPayment
        fields = ['amount', 'description']


class PaymentLinkSecCodeConfirmForm(forms.Form):
    code = forms.CharField(max_length=5, required=False)


class GoalSaveSave(forms.Form):
    to_save = forms.IntegerField(min_value=1)


class LinkSendEmail(forms.Form):
    email = forms.EmailField()


class WebTopUpLinkForm(forms.Form):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    birthday = forms.DateField(widget=forms.SelectDateWidget)
    card_number = forms.IntegerField()
    expiration = forms.IntegerField(max_value=9999)
    cvv = forms.IntegerField(max_value=999)
    tac = forms.BooleanField(widget=forms.CheckboxInput, required=True)


class MangoCardRegistrationForm(forms.Form):
    pass
