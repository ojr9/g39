from django.shortcuts import render, HttpResponseRedirect, HttpResponse, get_object_or_404, redirect
from django.views.generic import View, CreateView, DetailView, ListView, DeleteView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy

from saver.models import Saver
from cuenta.models import Cuenta
from .forms import MangoBankAccountForm, TopUpStartForm
from .models import MangoCardRegistration, MangoCard, MangoCardWebPayIn, MangoBankAccount, MangoPayOut, \
    MangoBankWirePayIn
from cuenta.models import Transaction


class MangoCardPreRegistrationView(View):
    def get(self, request, id):
        currency = Cuenta.objects.get(id=id).currency
        cr = MangoCardRegistration(currency=currency)
        context = {'preregdata': (cr.create(request.user))}
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


class TopUpStart(LoginRequiredMixin, View):
    def get(self, request, id):
        form = TopUpStartForm()
        return render(request, 'topup/create.html', {'form': form})

    def post(self, request, id):
        form = TopUpStartForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            account = get_object_or_404(Cuenta, id=id)
            saver = Saver.objects.get(user=request.user)
            if cd['payment_method'] == 'Card':
                cardpayin = MangoCardWebPayIn(saver=saver, amount=cd['amount'], currency=account.currency,
                                              statement_descriptor=cd['description'][:10], tag=cd['description'],
                                              return_url=request.build_absolute_uri(reverse('return')))

                result = cardpayin.create(account)
                # cardpayin.statement_descriptor = cd['description']
                # this doesn't work for some reason to create a custom descriptor
                return HttpResponseRedirect(result.RedirectURL)

            elif cd['payment_method'] == 'BW':
                bwpin = MangoBankWirePayIn(saver=saver, amount=cd['amount'], currency=account.currency,
                                           statement_descriptor=cd['description'])
                bwpin.create(account)
                # there are more params to pass in here, there is more to adapt and update in the model!!!!
                return render(request, 'topup/bwsummary.html', {'bw': bwpin})
            else:
                HttpResponse('The wrong payment was used or not recognized. Not card not bw, recheck.')


class CardWebPayinView(View):

    def get(self, request):
        mgppin = MangoCardWebPayIn.objects.get(piid=request.GET['transactionId'])
        pinnew = MangoCardWebPayIn.get_from_api(request.GET['transactionId'])

        if pinnew.status == 'SUCCEEDED':
            mgppin.status = 'SUCCESS'
            mgppin.result_code = 000000
            account = Cuenta.objects.get(wid=mgppin.cwid)
            account.deposit(mgppin.amount)
            message = messages.add_message(request, messages.SUCCESS, 'Payment was successful, thanks!')
            Transaction.objects.create(sender=request.user, receiver=request.user, receiver_account=account,
                                       amount=mgppin.amount, description=mgppin.tag, type='TopUp')
            # return HttpResponseRedirect(reverse('cuentaview', kwargs={'id': account.id, 'messages': message}))
            return render(request, 'cuenta/detail.html', {'id': account.id, 'messages': message})

        elif not pinnew.status == 'SUCCEEDED':
            mgppin.status = 'EXPIRED'
            mgppin.result_message = pinnew.result_message
            mgppin.result_code = pinnew.result_code
            mgppin.save()

            message = messages.add_message(request, messages.ERROR,
                                           message=('No charge was made. ' + mgppin.result_message))
            return render(request, 'payment/error.html', {'messages': message, 'payment': mgppin})
        else:
            HttpResponse('Something went wrong cause you arrived here. The api call didn\'t return or what the hell??')


class FileUploadKYC(View):
    # this is built into the Nat and Leg users, but here might be an interesting point to do that if the need arises.
    pass


class BankAccountCreateView(CreateView):
    model = MangoBankAccount
    template_name = 'bankaccount/create.html'
    form_class = MangoBankAccountForm
    success_url = reverse_lazy('saverview')

    def form_valid(self, form):
        form.instance.saver = Saver.objects.get(user=self.request.user)
        form.instance.save()
        cd = form.cleaned_data
        bankaccount = MangoBankAccount(saver=form.instance.saver, description=cd['description'], al1=cd['al1'],
                                       city=cd['city'], pc=cd['pc'], country=cd['country'],
                                       iban=cd['account_number'])
        bankaccount.create()
        # form.instance.create()
        # so this needs a form to create, not just the fields, cause the currency is by choices!
        # might need to change this it a normal View to create this easier...
        return super(BankAccountCreateView, self).form_valid(form)


def bankaccountdeleteview(request, ba_id):
    ba = get_object_or_404(MangoBankAccount, id=ba_id)
    saver = Saver.objects.get(user=request.user)
    if ba.saver == saver:
        ba.stop()
        ba.delete()
    return HttpResponseRedirect(reverse('saverview'))
