from django import forms
from django.urls import reverse_lazy

from allauth.account.forms import SignupForm
from mangopay.constants import LEGAL_USER_TYPE_CHOICES
from saver.models import Saver
from payment.models import MangoNaturalUser, MangoLegalUser

USER_TYPE_CHOICES = (('NAT', 'Private Person'), ('LEG', 'Any form of a legal entity'))


class UserSignupCustomForm(SignupForm):
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES, help_text='Are you registering a company or a private'
                                                                       ' person?')
    tac_accepted = forms.BooleanField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    # bd = forms.DateField(widget=forms.SelectDateWidget)
    # Add a nationality country field here

    def save(self, request):
        user = super(UserSignupCustomForm, self).save(request)
        user.first_name = request.POST['first_name']
        user.last_name = request.POST['last_name']
        # Just adding 1 to the Birthday for now. Will be updated in KYC in any case.
        # create a new form for the onboarding of a legal User
        mpu = MangoNaturalUser.objects.create(user=user, user_type=request.POST['user_type'])
        # mpu.birthday = request.POST['bd']
        mpu.create()
        # mpu.save()
        return user


class UpdateSaverForm(forms.ModelForm):
    front = forms.FileField(required=False, help_text='A clear, sharp picture of the front of your ID')
    back = forms.FileField(required=False, help_text='A clear, sharp picture of the back of your ID')

    class Meta:
        model = Saver
        fields = ['birthday', 'nationality', 'country_of_residence']


class LegalUserSignupCustomForm(SignupForm):
    user_type = forms.ChoiceField(choices=LEGAL_USER_TYPE_CHOICES, help_text='Are you an established BUSINESS, '
                                                                             'a non for profit ORGANIZATION or a'
                                                                             ' SOLETRADER?')
    # definitely add some more stuff here