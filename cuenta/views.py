# CRUD: GroupSave, Transaction
# LI+DET: GroupSave, Transaction --> make 2: for self obj, for api download
# topup, card reg, bank reg

from datetime import timedelta, datetime
# from django.utils.timezone import now, not sure this is the right one, but ok
# from segno import make
# import io
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy, reverse
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail, EmailMessage
from django.contrib.messages.views import SuccessMessageMixin
from django.core.files.base import ContentFile
from django.db.models.signals import post_save
from django.dispatch import receiver

from payment.models import MangoNaturalUser, MangoWallet
from .forms import GoalSaveCreateForm, GroupSaveCreateForm, Deposit, PaymentLinkCreateForm, \
    PaymentLinkSecCodeConfirmForm, GoalSaveSave, LinkSendEmail, WebTopUpLinkForm
from .models import Cuenta, GoalSaving, GroupSave, Transaction, LinkPayment
from payment.models import MangoCard

# This works well, but up to teh point where an infinite loop starts and generates a ton of image files until a timeout
# comes... Will comment out until later. Still not 100% sure why a QR code should be there in the view.
# Also, check if I have added teh QR code in the template.
# @receiver(post_save, sender=LinkPayment)
# def create_qr_for_link(**kwargs):
#     link = kwargs['instance']
#     out = io.BytesIO()
#     url = 'http://127.0.0.1:8000' + str(link.get_absolute_url(link.id))
#     img = make(url)
#     img.save(out, kind='png') # can add more params here.
#     link.qr_link.save((str(link.id) + '.png'), content=ContentFile(out.getvalue()), save=False)
#     link.save()
#     del img


def linkemailsend(link, email):
    message = f'Click here to access your payment link and pay: {link.get_absolute_url}'
    send_mail(f'Payment Link by G - {link.id}', message, 'link_sender@localhost', [email])


class IsOwnerMixin:
    def get_queryset(self, request):
        qs = super(IsOwnerMixin, self).get_queryset()
        return qs.filter(user=request.user)
    # sheesh, can't remember how to customize the function here... do I pass in the request after all?


# Cuenta CRUD - add flash messages and other signals later. It should work first

class CuentaCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Cuenta
    template_name = 'cuenta/create.html'
    fields = ['currency', 'description']
    success_message = 'Account successfully created'

    def form_valid(self, form):
        cd = form.cleaned_data
        accs = Cuenta.objects.filter(user=self.request.user, currency=cd['currency'])
        if len(accs) > 0:
            # Add message saying only 1 account per currency is available for now.
            return self.form_invalid(form)
        form.instance.user = self.request.user
        form.instance.save()
        wallet = MangoWallet(cuenta=form.instance)
        # wallet.save()
        wallet.create()
        return super().form_valid(form)


# no point in having an update view, there is nothing to update in these views,
# unless the account is emtpy and they want to delete


class CuentaDelete(LoginRequiredMixin, DeleteView):
    model = Cuenta
    success_url = reverse_lazy('cuentalist')
    template_name = 'cuenta/delete.html'
    context_object_name = 'account'


class CuentaList(LoginRequiredMixin, ListView):
    model = Cuenta
    template_name = 'cuenta/list.html'
    context_object_name = 'cuentas'

    def get_queryset(self):
        qs = super(CuentaList, self).get_queryset()
        return qs.filter(user=self.request.user)


class CuentaView(LoginRequiredMixin, DetailView):
    model = Cuenta
    template_name = 'cuenta/detail.html'
    pk_url_kwarg = 'id'
    # context_object_name = 'cuenta'

    def get_context_data(self, **kwargs):
        context = super(CuentaView, self).get_context_data()
        context['goals'] = GoalSaving.objects.filter(account=self.object)
        context['transactions'] = Transaction.objects.filter(receiver_account=self.kwargs['id'])
        context['links'] = LinkPayment.objects.filter(receiver_account=self.kwargs['id'])[:5]
        card = MangoCard.objects.filter(user=self.request.user, currency=self.object.currency)
        if card:
            context['form'] = Deposit(user=self.request.user, currency=self.object.currency) # is this syntax right?!

        # context['groupsaves'] ???
        # context['crowdfunds'] ???
        return context


@login_required
def deposit(request, id):
    if request.method == 'POST':
        account = get_object_or_404(Cuenta, id=id)
        form = Deposit(request.user, account.currency, request.POST)
        if form.is_valid():
            account.deposit(form.cleaned_data['amount'])
            if not form.cleaned_data['description']:
                form.cleaned_data['description'] = f'Deposit made on the {str(datetime.now())}'
            Transaction.objects.create(sender=request.user, receiver=request.user, receiver_account=account,
                                       amount=form.cleaned_data['amount'], description=form.cleaned_data['description'],
                                       type='TopUp')
            # message = messages.add_message(request, messages.SUCCESS, 'Deposit was successful')
            # No idea how to make the redirect here with the necessary args AND pass in the message as context
            # Choose a card here and make the deposit with it as part of the form!!
            # return render(request, 'cuenta/detail.html', {'id': id, 'messages': message})
            # return HttpResponseRedirect(reverse('cuentaview', kwargs={'id':id, 'message': message}))
            # This will need a try except part to make sure all is well, otherwise make an error.
            return HttpResponseRedirect(reverse('cuentaview', args=[id]))


# GoalSaving CRUD+DL
class GoalSavingCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = GoalSaving
    template_name = 'goals/create.html'
    form_class = GoalSaveCreateForm
    success_message = 'Goal successfully created'

    def form_valid(self, form):
        acc = Cuenta.objects.get(id=self.kwargs['id'])
        gc = GoalSaving.objects.filter(account=acc)
        if len(gc) > 4:
            return super().form_invalid(form)
        form.instance.account = acc
        # Send a check to the method check_monthly
        return super().form_valid(form)


class GoalSavingUpdate(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = GoalSaving
    template_name = 'goals/update.html'
    fields = ['title', 'description', 'monthly', 'image', 'video']
    success_message = 'Goal successfully updated'
    pk_url_kwarg = 'goal_id'
#     call a function in the model to take fees if the goal is altered down.


class GoalSavingAbort(LoginRequiredMixin, DeleteView):
    model = GoalSaving

    def get_success_url(self):
        return reverse_lazy('cuentaview', args=[self.kwargs['goal_id']])


class GoalSavingDetail(LoginRequiredMixin, DetailView):
    model = GoalSaving
    template_name = 'goals/detail.html'
    pk_url_kwarg = 'goal_id'
    context_object_name = 'goal'

    def get_context_data(self, **kwargs):
        context = super(GoalSavingDetail, self).get_context_data()
        context['id'] = self.kwargs['id']
        context['form'] = GoalSaveSave
        return context


@login_required
def savetogoal(request, id, goal_id):
    if request.method == 'POST':
        form = GoalSaveSave(data=request.POST)
        if form.is_valid():
            goal = get_object_or_404(GoalSaving, id=goal_id)
            account = get_object_or_404(Cuenta, id=id)
            amount = form.cleaned_data['to_save']
            if amount <= goal.account.balance:
                goal.add_from_account(account, amount)
                Transaction.objects.create(sender=request.user, sender_account=account, receiver=request.user,
                                           description=f'Lock in from the account to {goal}', receiver_account=account,
                                           amount=amount, type='ToGoal')
                return HttpResponseRedirect(reverse('goalsaveview', kwargs={'id': account.id, 'goal_id': goal.id}))
            else:
                return HttpResponse("trying to add mroe towards the goal than what is available in the account. This else is a pain in the ass")


class PaymentLinkCreate(LoginRequiredMixin, CreateView):
    model = LinkPayment
    template_name = 'links/create.html'
    form_class = PaymentLinkCreateForm

    def form_valid(self, form):
        form.instance.receiver = self.request.user
        form.instance.receiver_account = Cuenta.objects.get(id=self.kwargs['id'])
        form.instance.expiry = timedelta(days=60)
        linkemailsend(link=form.instance, email=form.cleaned_data['email'])
        return super(PaymentLinkCreate, self).form_valid(form)

    def get_success_url(self):
        acc = Cuenta.objects.get(id=self.kwargs['id'])
        return reverse_lazy('cuentaview', args=[acc.id])


class PaymentLinkList(LoginRequiredMixin, ListView):
    model = LinkPayment
    template_name = 'links/list.html'
    context_object_name = 'links'

    def get_queryset(self):
        qs = super(PaymentLinkList, self).get_queryset()
        return qs.filter(receiver=self.request.user)


class PaymentLinkListView(LoginRequiredMixin, View):
    def get(self, request, id):
        links = LinkPayment.objects.filter(receiver_account=id)
        return render(request, 'links/list.html', {'links': links})


# Add a check and logic for logged in users. if not add a form for a webpayin or something like that
class LinkView(View):
    # This is the view for the sender to make the payment.
    def get(self, request, pl_id):
        link = LinkPayment.objects.get(id=pl_id)
        account = link.receiver_account
        form = PaymentLinkSecCodeConfirmForm()
        context = {'link': link, 'account': account, 'form': form}
        return render(request, 'links/detail.html', context)

    def post(self, request, pl_id):
        # Add a check and logic for logged in users. if not add a form for a webpayin or something like that
        form = PaymentLinkSecCodeConfirmForm(data=request.POST)
        if form.is_valid():
            code = int(form.cleaned_data['code'])
            link = LinkPayment.objects.get(id=pl_id)
            if not request.user.is_authenticated:
                return HttpResponseRedirect('webtopup', kwargs={'pl_id': pl_id})
            try:
                sender_account = Cuenta.objects.get(user=request.user, currency=link.receiver_account.currency)
            except:
                message = messages.add_message(request, messages.INFO, 'Please create an account in the requested '
                                                                       'currnecy')
                return HttpResponseRedirect(reverse('cuentacreate'), kwargs={'messages': message})

            if link.selfpay_check(request.user) is False:
                message = messages.add_message(request, messages.ERROR, 'You cannot pay your own link.')
                return HttpResponseRedirect(reverse('linklist', kwargs={'messages': message, 'id': link.receiver_account.id}))
            elif link.code_check(code) is False:
                message = messages.add_message(request, messages.INFO, 'Security code incorrect.')
                return HttpResponseRedirect(reverse('linkview', kwargs={'messages': message, 'pl_id': pl_id}))
            # elif link.has_acc_check(request.user) is False:
                # message = messages.add_message(request, messages.INFO,
                #                                'You need an account in this currency to make a payment. Later cross'
                #                                ' currency will be added...')

            elif link.amount_check(sender_account.balance) is False:
                # message = messages.add_message(request, messages.INFO,
                #                                'Please add more funds to your account, to make the payment')
                return HttpResponseRedirect(reverse('cuentacreate'))
            else:
                link.pay(user=request.user, sender_account=sender_account)
                Transaction.objects.create(sender=request.user, receiver=link.receiver,
                                           receiver_account=link.receiver_account, amount=link.amount,
                                           description=f'Link payment {link.description}', type='LinkPayment')
            return render(request, 'links/paid.html', {'link': link})


# This view can create a base for a card web payin, just need to add it to the thing here.
class WebTopUpLinkPay(View):
    def get(self, request, pl_id):
        form = WebTopUpLinkForm()
        link = LinkPayment.objects.get(id=pl_id)
        context = {'form': form, 'link': link}
        return render(request, 'webtopup/create.html', context)

    def post(self, request, pl_id):
        form = WebTopUpLinkForm(data=request.POST)
        if form.is_valid():
            return HttpResponse('post was valid')


class LinkSendPreV(LoginRequiredMixin, View):
    # This is the preview of the link before sending it.
    def get(self, request, pl_id):
        link = get_object_or_404(LinkPayment, id=pl_id)
        form = LinkSendEmail()
        return render(request, 'links/preview.html', {'link': link, 'form': form})

    def post(self, request, pl_id):
        form = LinkSendEmail(data=request.POST)
        if form.is_valid():
            link = get_object_or_404(LinkPayment, id=pl_id)
            message = f'Click here to access your payment link and pay: {link.get_absolute_url}'
            send_mail(f'Payment Link by G - {link.id}', message, 'link_sender@localhost', [form.cleaned_data['email']])
            # add a success message here.
            return HttpResponseRedirect(reverse('linklist', args=[link.receiver_account.id]))


@login_required
def cancellink(request, pl_id):
    # Add a check to see that only the link owner can cancel these. 
    link = get_object_or_404(LinkPayment, id=pl_id)
    id = link.receiver_account.id
    link.delete()
    return HttpResponseRedirect(reverse('linklist', args=[id]))
