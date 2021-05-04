import uuid
import datetime
from random import randint
from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User

from saver.models import Saver
from mangopay.resources import BankingAliasIBAN
# Link to SAVER or to User??? It's starting to look like Saver?!! mangousers & cards were the case
# Actually migrate this to another app!!!

supported_currencies = (('EUR', 'Euro'), ('USD', 'USD'), ('CHF', 'Swiss Franc'))
statuses = (('CREA', 'CREATED'), ('PROG', 'IN PROGRESS'), ('ACCO', 'ACCOMPLISHED'), ('TERM', 'TERMINATED'))


class Cuenta(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    id = models.CharField(max_length=35, default=uuid.uuid4, primary_key=True, editable=False, db_index=True)
    # Convert to UUID fields in deployment
    activation = models.BooleanField(default=True)
    viban = models.CharField(max_length=35, null=True)
    # bic = models.CharField(max_length=10) needs a migration to be in
    currency = models.CharField(max_length=3, choices=supported_currencies, default='EUR')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    wid = models.IntegerField(verbose_name='Wallet ID', default=0)
    description = models.CharField(max_length=200)

    def get_absolute_url(self):
        return reverse('cuentaview', args=[self.id])

    def __str__(self):
        return f'{self.user} - {self.currency}'

    def deposit(self, amount):
        self.balance += amount
        self.save()

    # def _transfer(self, receiver, sender, amount, currency):
    #     racc = Cuenta.objects.get(user=receiver, currency=currency)
    #     sacc = Cuenta.objects.get(user=sender, currency=currency)
    #     racc.deposit(amount)

    def check_balance(self, amount):
        if self.balance < amount:
            return False
        return True

    def _ibanize(self, country='LU'):
        saver = Saver.objects.get(user=self.user)
        alias = BankingAliasIBAN(WalletId=self.wid, Country=country, credited_user=saver.mid)
        alias.save()
        self.viban = alias['IBAN']
        # see in the docs if there is any other useful field for here...
        self.save()

    def account_deactivate(self):
        self.activation = False
        self.save()


class GoalSaving(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    account = models.ForeignKey(Cuenta, on_delete=models.CASCADE)
    title = models.CharField(max_length=25)
    description = models.TextField(help_text='Add a description if you like, here', blank=True, null=True)
    goal = models.IntegerField(validators=(MinValueValidator(250, message='Minimum amount is 250.'),))
    achieved = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    monthly = models.DecimalField(max_digits=8, decimal_places=2, null=True, default=0.00,
                                  help_text='Want to add a monthly topup amount? Leave at 0 if not.')
    status = models.CharField(max_length=4, choices=statuses, default='CREA')
    image = models.ImageField(upload_to='images/goals/', blank=True, null=True)
    video = models.URLField(null=True, blank=True)
    duration = models.DurationField()

    def __str__(self):
        return f'{self.title} - {self.account}'

    @staticmethod
    def check_monthly(goal, monthly):
        if goal % 2 < monthly:
            return False
        return True

    def update(self):
       pass
    # really not see how to best define the updater, when a deposit is made
    # make some more to control the point in time when a goal is achieved and
    # therefore ok to be paid out or something. Still not sure about the methods here.

    def get_absolute_url(self):
        return reverse('goalsaveview', kwargs={'id': self.account.id, 'goal_id': self.id})

    def add_from_account(self, account, amount):
        acc = Cuenta.objects.get(id=account.id)
        self.achieved += amount
        acc.balance -= amount
        self.save()
        acc.save()


class GroupSave(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    members = models.ManyToManyField(User, related_name='group-save-members+') # or make the link withthe Saver
    account = models.OneToOneField(Cuenta, on_delete=models.PROTECT)
    title = models.CharField(max_length=250)
    description = models.TextField(help_text='Add a description if you like, here', blank=True, null=True)
    goal = models.IntegerField(validators=(MinValueValidator(250, message='Minimum amount is 250.'),))
    achieved = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    monthly = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=4, choices=statuses, default='CREA')
    image = models.ImageField(upload_to='images/goals/', blank=True, null=True)
    video = models.URLField(null=True, blank=True)

    def __str__(self):
        return f'{self.pk} - {self.title}'


class LinkPayment(models.Model):
    STATUS = (('WAIT', 'Awaiting Payment'), ('PAID', 'Payment Successful'), ('CANC', 'Link Cancelled'),
              ('EXPR', 'Link Expired'))

    created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=4, choices=STATUS, default='WAIT')
    receiver = models.ForeignKey(Saver, on_delete=models.CASCADE, related_name='receiverForLink')
    receiver_account = models.ForeignKey(Cuenta, on_delete=models.CASCADE, related_name='receiverAccount')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender', null=True)
    expiry = models.DurationField(editable=False)
    description = models.CharField(max_length=35)
    execution = models.DateTimeField(blank=True, null=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.01, validators=(MinValueValidator(0.01),))
    sec_code = models.PositiveSmallIntegerField(editable=False, default=randint(10000, 99999))
    qr_link = models.ImageField(upload_to='static/qr_links/', null=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.description

    def selfpay_check(self, user):
        if user is self.receiver:
            return False
        return True

    def code_check(self, code):
        if code == self.sec_code:
            return True
        return False

    def has_acc_check(self, user):
        sender_acc = Cuenta.objects.get(user=user, currency=self.receiver_account.currency)
        if sender_acc is None:
            return False
        return True

    def amount_check(self, balance):
        if balance < self.amount:
            return False
        return True

    def pay(self, user, sender_account):
        sender_account.balance -= self.amount
        # Insert a transfer here, from the payments model
        self.receiver_account.deposit(self.amount)
        self.status = 'PAID'
        self.execution = datetime.datetime.utcnow()
        self.sender = user
        self.save()
    #     Have to assign the payer as payer, teh execution date as now, the status as PAID, and update the wallet
    #     amounts.

    def erase(self):
        return self.delete()

    def get_absolute_url(self, pl_id):
        return reverse('linkview', args=[pl_id])
#     How do I know when clicking on one from outside, what self is?! Here I''m telling args, but inreality they should
#     Be passed in through the url? hmm actually just for the receiver, when going through the account, otherwise it
#     would not be the case at all. This should be right, but not 100% sure.


class Transaction(models.Model):
    """
    This model is to document transactions. The type of transaction according to the use, either, a topup, link,
    goal, etc. Cuentas can always by synced from the API but that flow if information right into the account I'd
    really rather avoid. The problem is then the coordination of information... there can be both tne DB on my side and
    on the API side, but the right syncro is then the main issue. How do you sync? Well at least have minimum the
    same data structure and know the ID in the APi. The alternative is a ton of API GETs...
    """
    TYPES = (('TopUoooop', 'TopUphahah  '), ('Donation', 'Donation'), ('LinkPayment', 'LinkPayment'),
             ('ToGoal', 'Added to Goal'))

    created = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(User, on_delete=models.PROTECT, related_name='sender-user+')
    sender_account = models.ForeignKey(Cuenta, on_delete=models.PROTECT, related_name='sender-account+', blank=True,
                                   null=True)
    receiver = models.ForeignKey(User, on_delete=models.PROTECT, related_name='receiver-user+')
    receiver_account = models.ForeignKey(Cuenta, on_delete=models.PROTECT, related_name='receiver-account+')
    amount = models.DecimalField(max_digits=7, decimal_places=2,
                                 validators=[MinValueValidator(50, message='50 is the minimum value here'), ])
    description = models.CharField(max_length=150, blank=True, null=True)
    type = models.CharField(max_length=11, choices=TYPES)

    class Meta:
        ordering = ['-created']

