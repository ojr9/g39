from django.shortcuts import render, HttpResponseRedirect, reverse, HttpResponse
from django.views.generic import View, CreateView
from django.contrib import messages

from saver.models import Saver
from cuenta.models import Cuenta
from payment.models import MangoCardRegistration, MangoCard, MangoCardWebPayIn


class MangoCardPreRegistrationView(View):
    def get(self, request, id):
        currency = Cuenta.objects.get(id=id).currency
        cr = MangoCardRegistration(currency=currency)
        cr.create(request.user)
        context = {}
        context['preregdata'] = cr.create(request.user)
        # Append more stuff to the context here if needed, or in the dict in the model.
        return render(request, 'cards/create.html', context)
    # the def post() will be done via the form in the template with JS. Do I need to load it here??


class MangoCardRegistrationView(View):
    def get(self, request, id, data):
        registration = MangoCardRegistration.objects.get(id=id)
        registration._update(data)
        return render(request, 'the template for a card when done?')


class MangoCardView(View):
    pass


def ibanize(request, id):
    cuenta = Cuenta.objects.get(id=id)
    cuenta._ibanize()
    # add some logic here, like extra fee or whatever....
    return HttpResponseRedirect(reverse('cuentaview', kwargs={'id': id}))


def cardwebinit(request, account, amount, currency):
    mgppin = MangoCardWebPayIn(retun_url=reverse('return'), money=(amount, currency))
    mgppin.create(request.user, account)
    # see the docs to make a custom page like in leetchi


class CardWebPayinView(View):
    # Alternatively to this, create the _check_payin method and go from there.
    def get(self, request, piid):
        mgppin = MangoCardWebPayIn.objects.get(id=piid)
        if mgppin['result_code'] == 000000:
            # Add soem if to see if there's something to do with the user, like display
            # the message in the account list page orsomething, cause a full template?! hmm maybe for some confirmation?
            message = messages.add_message(request, messages.SUCCESS, 'Payment was successful, thanks!')
            return render(request, 'payment/thanks.html', {'messages': message, 'payment': mgppin})
        elif mgppin['result_code'] != 000000:
            message = messages.add_message(request, messages.ERROR, message=mgppin['result_message'])
            return render(request, 'payment/error.html', {'messages': message, 'payment': mgppin})
        else:
            HttpResponse('Something went wrong cause you arrived here. The api call didn\'t return or what the hell??')


class FileUploadKYC(View):
    pass
