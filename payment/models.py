import datetime
import base64
import json

from django.db import models
from django.shortcuts import HttpResponse, redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth import get_user_model

from mangopay.constants import USER_TYPE_CHOICES, CARD_TYPE_CHOICES, PAYMENT_STATUS_CHOICES, LEGAL_USER_TYPE_CHOICES, \
    TRANSACTION_TYPE_CHOICES, SECURE_MODE_CHOICES
from mangopay.utils import timestamp_from_datetime, timestamp_from_date, Money, Address # see if these are needed or better use django
from mangopay.resources import NaturalUser, LegalUser, Wallet, Transfer, Card, CardRegistration, BankWirePayIn,\
    BankingAliasIBAN, DirectPayIn, CardWebPayIn, GooglepayPayIn, ApplepayPayIn, PreAuthorization, \
    PreAuthorizedPayIn, BankAccount, BankWirePayOut, BankWirePayInExternalInstruction, TransferRefund, PayInRefund, \
    Document, Page, Ubo, UboDeclaration
    # there are quite some resources here that I don't think I'll ever want to use, but let's start with the main ones
    # and see where the road goes.
from saver.models import Saver
from cuenta.models import Cuenta, LinkPayment, GoalSaving


"""
Design notes: The calls to the api are done here, for all end points. 
For the users, Natural adn Legal, they subclass the Saver class, as the one class that should hold all data between the 
models, and then should be the base for the users here. 
All other classes here are independent of the objects they support in the main apps. Let's see which of both approaches
works best. In the case of the user, pass params to the Class of MPG as self.<param>, in the others 
self.<1to1fieldlink>.<param>
The api calls are always fired in the same way, from a create() method in the class. The view or the form will 
instatiate the object of this list of models, and call the method. On that object class, add more methods for other 
functions related, like checking, updating, etc.   
In the testing and integrating this all, before I call create(), I can always call save(). This is the save from django.
It completes all except the api call, good for offline testing.
"""

supported_currencies = (('EUR', 'Euro'), ('USD', 'USD'), ('CHF', 'Swiss Franc'))
usr = get_user_model()


def _money_format(amount):
    if isinstance(amount, float):
        return int(amount) * 100
    elif isinstance(amount, int):
        return amount/100
    else:
        return HttpResponse('Money amount is neither int nor float')
    # Is the logic clear here?


def change_make_timestamp(datetimeobject):
    if isinstance(datetimeobject, datetime.datetime) or isinstance(datetimeobject, datetime.date):
        return timestamp_from_date(datetimeobject)
    elif isinstance(datetimeobject, int):
        return datetimeobject
    else:
        raise TypeError


def _make_timestamp(data):
    if isinstance(data, datetime.date):
        return timestamp_from_date(data)


def _from_timestamp(ts):
    if isinstance(ts, str):
        return datetime.datetime.fromtimestamp(int(ts), None)
    elif isinstance(ts, int):
        return datetime.datetime.fromtimestamp(ts, None)
    else:
        raise TypeError


class MangoNaturalUser(Saver):

    def create(self):
        if not self.birthday or self.birthday == 0:
            db = 1
        else:
            db = _make_timestamp(self.birthday)
        mango_call = NaturalUser(FirstName=self.user.first_name, LastName=self.user.last_name, Email=self.user.email,
                                 Birthday=db, Nationality=self.nationality,
                                 CountryOfResidence=self.country_of_residence)

        mango_call.save()
        self.mid = mango_call.Id
        # Add more data from the return of the call
        self.save()

    def _validated(self):
        mpu = NaturalUser.get(id=self.mid)
        # mpu need to do stuff here!!!
        # sdlkfjas ldkf ;slakdjfsd jfasd fs asd
        #lkashd fshdf kajs hdklasfh
        # klajsdf laksd flasdh flak sd

        return self.validation_status

    def validate(self, document_type, front, back):
        if not self.validation_status == 'VALIDATED':
            doc = Document(type='IDENTITY_PROOF', user=self.mid)
            doc.save()

            with open(front, 'rb') as f:
                encf = base64.b64decode(f.read())

            with open(back, 'rb') as b:
                encb = base64.b64encode(b.read())

            pf = Page(document=doc, file=encf, user=self.mid)
            pf.save()

            pb = Page(document=doc, file=encb, user=self.mid)
            pb.save()

            doc.status = 'VALIDATION_ASKED'
            doc.save()
            print(doc)
            # see if this validation works or if the last step is necessary.
        else:
            return 'Documents have been already validated'

    def get_docs_list(self):
        mpu = NaturalUser.get(self.mid)
        docs = mpu.documents.all()
        for d in docs:
            print(d)
        return docs
        # check for validation and status of each, see what comes back here

    def __str__(self):
        return str(self.mid)


class MangoLegalUser(Saver):
    legal_type = models.CharField(max_length=35, choices=LEGAL_USER_TYPE_CHOICES)
    legal_name = models.CharField(max_length=150)
    legal_rep_email = models.EmailField(null=True)
    company_number = models.CharField(max_length=150, null=True)

    def create(self):
        mango_call = LegalUser(LegalPersonType=self.legal_type, Name=self.legal_name,
                               LegalRepresentativeBirthday=_make_timestamp(self.birthday), # see if this self. is right?
                               LegalRepresentativeCountryOfResidence=self.country_of_residence,
                               LegalRepresentativeNationality=self.nationality,
                               LegalRepresentativeFirstName=self.user.first_name,
                               LegalRepresentativeLastName=self.user.last_name, Email=self.user.email,
                               CompanyNumber=self.company_number)
        mango_call.save()
        self.mid = mango_call.Id
        self.save()

    def _add_legal_rep_email(self, email):
        self.legal_rep_email = email
        # See in the form that it is a valid email! Update the api entry?
        self.save()


class MangoWallet(models.Model):

    cuenta = models.OneToOneField(Cuenta, on_delete=models.PROTECT, related_name='cuenta_wallet')
    # make some more fields here?

    def create(self):
        # get the mid here? rather here, but eaiser in view
        saver = Saver.objects.get(user=self.cuenta.user)
        wallet_call = Wallet(Owners=[saver.mid], Description=self.cuenta.description, currency=self.cuenta.currency)
        wallet_call.save()
        self.cuenta.wid = wallet_call.Id # make sure an int is returned here.
        print(self.cuenta.wid)
        print(wallet_call.Id)
        self.save()

    def update_wallet(self):
        if not self.cuenta.wid:
            wallet = Wallet.get(self.cuenta.wid)
            wallet.update(self.cuenta.wid, Description=self.cuenta.description)
            wallet.save()

    def get_balance(self):
        wallet = Wallet.get(self.cuenta.wid)
        if self.balance != wallet.Balance.Amount / 100:
            self.balance = wallet.Balance.Amount / 100
            self.save()
        return self.balance, self.currency

    def __str__(self):
        return f'Wallet {self.cuenta.wid} from {self.cuenta}'

    def _ibanize(self, country='LU'):
        alias = BankingAliasIBAN(WalletId=self.cuenta.wid, Country=country)
        alias.save()
        self.cuenta.viban = alias['IBAN'] # is this really or should this be alias.IBAN??
        self.save()
        # When more vIBANs are there update to choose from them

    # using hte sdk like this is shit, this is still a bit too hard...
    # def view_iban(self):
    #     wallet = Wallet.get(self.cuenta.wid)


class MangoCard(models.Model):
    cid = models.PositiveIntegerField(default=0)
    saver = models.ForeignKey(Saver, on_delete=models.CASCADE, related_name='mangocard')
    expiration_date = models.PositiveSmallIntegerField(default=0)
    currency = models.CharField(max_length=3, default='EUR')
    alias = models.CharField(max_length=20, default='')
    provider = models.CharField(max_length=15, default='')
    card_type = models.CharField(max_length=20, choices=CARD_TYPE_CHOICES)
    is_active = models.BooleanField(default=False)
    is_valid = models.BooleanField(default=False)
    creation_date = models.PositiveIntegerField(default=0) #this needs to change to a date field that gets a time stamp
    fingerprint = models.CharField(max_length=100, default='call update function')

    # deleted = models.BooleanField(default=False) this was extra in the integration example
    def deactivate(self):
        # card = Card.get(self.cid)
        # do I have to make a custom call here to deactivate?? where is the function in the sdk??
        pass

    def list_all_user_cards(self):
        pass

    def update_from_api(self):
        # Am I getting here the first cid? then no if
        if self.cid:
            card = Card.get(self.cid)
            self.expiration_date = card.ExpirationDate
            self.alias = card.Alias
            self.provider = card.CardProvider
            self.currency = card.Currency
            if card.Active == '':
                self.is_active = True
            if card.Validity == 'VALID':
                self.is_valid = True
            self.creation_date = card.CreationDate
            self.fingerprint = card.fingerprint
            self.card_type = card.CardType
            self.save()

    def is_expired(self):
        month = self.expiration_date[:2]
        year = self.expiration_date[2:]
        current_month = datetime.datetime.utcnow().month
        current_year = int(str(datetime.datetime.utcnow().year)[2:])
        if current_year > year:
            return True
        if current_year == year and current_month >= month:
            return True
        return False

    def __str__(self):
        return f'{self.cid} from {self.saver}'


class MangoCardRegistration(models.Model):
    crid = models.PositiveIntegerField(default=0)
    currency = models.CharField(max_length=3, default='EUR')
    card_type = models.CharField(max_length=20, default=CARD_TYPE_CHOICES['CB_VISA_MASTERCARD'])
    card = models.OneToOneField(MangoCard, on_delete=models.CASCADE, related_name='mangocardregistration', null=True)

    def create(self, user):
        saver = Saver.objects.get(user=user)
        registration = CardRegistration(UserId=saver.mid, Currency=self.currency)
        registration.save()
        print(registration.Id)
        self.crid = registration.Id
        # Create the card that will hold all the data once registration is done
        if not self.card:
            card = MangoCard(saver=saver, currency=self.currency, is_valid=True, card_type=self.card_type)
            card.save()
            self.card = card
            if not self.card:
                return HttpResponse('card in thingy not beign saved')
        # Now the preregistration data should be in the 'registration' variable. Passing this back to the view.
        preregdata = {'AccessKey': registration.AccessKey, 'PreregistrationData': registration.PreregistrationData,
                      'CardRegistrationURL': registration.CardRegistrationURL, 'CardRegId': self.crid}
        return preregdata

    def _update(self, data):
        reg = CardRegistration.get(self.crid)
        reg.update(data)
        reg.save()
        crd = MangoCard.objects.get(self.card)
        crd.cid = reg.Id
        crd.expiration_date = reg.ExpirationDate
        crd.alias = reg.Alias
        crd.creation_date = reg.CreationDate
        crd.fingerprint = reg.Fingerprint
        crd.save()


class MangoPreAuth(models.Model):
    pass
# requires a working registered card


class MangoTransfer(models.Model):
    tid = models.IntegerField()
    saver = models.ForeignKey(Saver, on_delete=models.DO_NOTHING, related_name='savertransfer')
    status = models.CharField(max_length=9, default='Paid', blank=True, null=True)
    # Change the last one to to a default value adn see if the choices are right
    execution_date = models.DateTimeField(blank=True, null=True)
    credited_cuenta = models.OneToOneField(Cuenta, on_delete=models.PROTECT, related_name='transfercreditedaccount')
    debited_cuenta = models.OneToOneField(Cuenta, on_delete=models.PROTECT, related_name='transferdebitedaccount')
    # The link needs to improve!!! like sending money to multiple people, not just
    # 1 on 1!! There is a big improvement to do here!
    # And / or send money to a group? Not even sure right now what Groups will be like.
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    fees = models.DecimalField(max_digits=6, decimal_places=2)

    currency = models.CharField(max_length=3, choices=supported_currencies, default='EUR')

    def create(self):
        transfer = Transfer(AuthorId=self.saver.mid, DebitedFunds=Money(self.amount, self.currency),
                            Fees=Money(msdfsdfsdfsdfsdf(self.amount*0.05), self.currency),
                            DebitedWalletId=self.debited_cuenta.wid, CreditedWalletId=self.credited_cuenta.wid)

        transfer.save()
        self.tid = transfer.Id
        #try the Id thingy like this.
        self.execution_date = datetime.datetime.fromtimestamp(transfer.execution_date)
        self.save()
    # set execution date from timestamp to normal


class MangoPayIn(models.Model):

    piid = models.PositiveIntegerField(default=0)
    creation_date = models.DateTimeField()
    saver = models.ForeignKey(Saver, on_delete=models.PROTECT, related_name='%(class)s_mango_payin_author')
    cwid = models.PositiveIntegerField(default=0)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    fees = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3, default='EUR')
    culture = models.CharField(max_length=2, default='EN')
    statement_descriptor = models.CharField(max_length=12, default='')
    status = models.CharField(max_length=9, choices=PAYMENT_STATUS_CHOICES, default='CREATED')
    result_code = models.CharField(max_length=6, null=True, blank=True)
    result_message = models.CharField(max_length=255, null=True, blank=True)
    # execution_date
    nature = models.CharField(max_length=10, default='')
    transaction_type = models.CharField(max_length=10)
    tag = models.CharField(max_length=254, blank=True, null=True)

    class Meta:
        ordering = ['creation_date']


class MangoCardWebPayIn(MangoPayIn):
    return_url = models.URLField() # this needs to change to a permanent address that has no params in the url!? no it ahs 3
    card_type = models.CharField(max_length=20, choices=CARD_TYPE_CHOICES, default='CB_VISA_MASTERCARD')
    secure_mode = models.CharField(max_length=9, choices=SECURE_MODE_CHOICES, default=SECURE_MODE_CHOICES['DEFAULT'])
    # money = MoneyField()

    def retry(self):
        # depending on the result codes, some logic here to retry or not.
        pass

    def create(self, account):
        # Only CB_VISA_MC is accepted for now
        am = float(self.amount)
        if am > 50.0 and not self.secure_mode == SECURE_MODE_CHOICES['DEFAULT']:
            self.secure_mode = SECURE_MODE_CHOICES[1]

        self.cwid = account.wid
        self.fees = round(am * 0.1, 2)

        am = am * 100
        fe = self.fees*100
        payin = CardWebPayIn(AuthorId=self.saver.mid,
                             DebitedFunds=Money(amount=am, currency=self.currency),
                             Fees=Money(amount=fe, currency=self.currency),
                             ReturnURL=self.return_url,
                             CardType=self.card_type,
                             CreditedWalletId=self.cwid,
                             SecureMode=self.secure_mode,
                             Culture=self.culture,
                             StatementDescriptor=self.statement_descriptor,
                             tag=self.tag)
        payin.save()
        self.piid = payin.Id
        self.status = payin.Status
        # self.creation_date = _from_timestamp(payin.CreationDate)
        self.creation_date = datetime.datetime.now()
        # do I need to do something like response.json() to dump the strings and use them???
        self.save()
        if payin.RedirectURL:
            return payin
        return HttpResponse('redirect failed, if-condition not met')

    def get_from_api(piid):
        return CardWebPayIn.get(piid)

    def get_absolute_url(self):
        return reverse('return', args=[self.piid])

    def __str__(self):
        return f'Card Web topUp {self.piid}'


class MangoCardDirectPayIn(MangoPayIn):
    card = models.ForeignKey(MangoCard, on_delete=models.DO_NOTHING, related_name='mangodirectpayinscard')

    def create(self, user, account):
        pass

    def __str__(self):
        return f'Deposit with card: {self.card} - {self.amount} on {self.creation_date}'


# Don't think an address is needed here for the payin, it will be for the payout though.
class MangoBankWirePayIn(MangoPayIn):
    execution_type = models.CharField(max_length=50)
    wire_reference = models.CharField(max_length=50)
    wire_type = models.CharField(max_length=5)
    iban = models.CharField(max_length=50) # Need to change this to an IBAN field, same as above.
    bic = models.CharField(max_length=25)

    def create(self, account):
        self.cwid = account.wid
        self.fees = round(float(self.amount) * 0.1, 2)

        am = self.amount * 100
        fe = self.fees * 100
        bw = BankWirePayIn(AuthorId=self.saver.mid, CreditedWalletId=account.wid,
                           DeclaredDebitedFunds=Money(am, account.currency),
                           DeclaredFees=Money(fe, account.currency))
        bw.save()
        self.piid = bw.Id
        # self.creation_date = bw.CreationDate
        # self.creation_date = _from_timestamp(bw.CreationDate)
        self.creation_date = datetime.datetime.now()
        self.status = 'CREATED'
        self.transaction_type = bw.BANK_WIRE
        self.wire_reference = bw.WireReference
        self.wire_type = bw.Type
        self.iban = bw.IBAN
        self.bic = bw.BIC
        self.save()

    def _check_status(self):
        bw = BankWirePayIn.get(Id=self.piid)
        if bw.status != self.status:
            self.status = bw.status
        return self.status

    def __str__(self):
        return f'{self.piid} BW on {self.creation_date} - {self.status}'


class MangoBankAccount(models.Model):
    saver = models.ForeignKey(Saver, on_delete=models.DO_NOTHING, related_name='saverbankaccount')
    bid = models.PositiveIntegerField(default=0)
    description = models.CharField(max_length=25)
    bank_account_type = models.CharField(max_length=6, default='IBAN')
    al1 = models.CharField(max_length=150)
    al2 = models.CharField(max_length=150, null=True, blank=True)
    city = models.CharField(max_length=50)
    pc = models.CharField(max_length=8)
    country = models.CharField(max_length=25) #change for a country field later on.
    account_number = models.CharField(max_length=50)
    bic = models.CharField(max_length=12, blank=True, null=True)
    iban = models.CharField(max_length=25)
    currency = models.CharField(max_length=3, default=supported_currencies)

    def _make_address(self):
        return Address(address_line_1=self.al1, address_line_2=self.al2, city=self.city, postal_code=self.pc,
                       country=self.country)

    def create(self):
        # Instead of getting the NaturalUser, I can get Saver! like that I can query both Natural and Legal, when I have
        # the model utils manager installed !!! Now this makes sense why to have it and how to use it!
        # Also because the MIDs are unique for all MP Objects. Makes it simpler, but only easier to see in hindsight!!

        ba = BankAccount(owner_name=(self.saver.user.first_name + '' + self.saver.user.last_name),
                          user_id=self.saver.mid, type=self.bank_account_type, owner_address=self._make_address(),
                         IBAN=self.iban, BIC=self.bic)
        ba.save()
        self.bid = ba.Id
        # get other stuff from the API to add to the model?
        self.save()

    def __str__(self):
        return self.description

    def stop(self):
        if not self.bid == 0:
            ba = BankAccount.get(id=self.bid) # something is fishy here: needs a reference???
            ba.deactivate()


class MangoPayOut(models.Model):

    poid = models.PositiveIntegerField(default=0)
    creation_date = models.DateTimeField(auto_now_add=True)
    saver = models.ForeignKey(Saver, on_delete=models.PROTECT, related_name='savermangopayout')
    dwid = models.ForeignKey(MangoWallet, on_delete=models.PROTECT, related_name='dwidmangopayout')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    fees = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3, default='EUR')
    culture = models.CharField(max_length=2, default='EN')
    statement_descriptor = models.CharField(max_length=12, default='')
    # status = models.CharField(max_length=9, choices=(), default='CREATED')
    result_code = models.CharField(max_length=6, null=True, blank=True)
    result_message = models.CharField(max_length=255, null=True, blank=True)
    # execution_date
    nature = models.CharField(max_length=10, default='')
    transaction_type = models.CharField(max_length=10)
    # pullled these straight outta thin air. Check against docs!
    bank_wire_ref = models.CharField(max_length=150) # is this like a description???

    def check_status(self):
        return f'{self.status} - {self.result_message}'

    def create(self):
        # mpu = Saver.objects.get(self.author)
        ba = MangoBankAccount.objects.get(owner=self.saver.mid)
        po = BankWirePayOut(author=self.saver.mid, debited_funds=Money(amount=self.amount, currency=self.currency),
                            debited_wallet=self.dwid, bank_account=ba.bid, bank_wire_ref=self.bank_wire_ref)
        po.save()
        self.poid = po.get_pk()
        # get other stuff from the api call and add accordingly
        self.save()

    def __str__(self):
        return self.poid
    # add some other methods here.

