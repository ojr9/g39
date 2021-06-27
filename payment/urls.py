from django.urls import path

from .views import MangoCardRegistrationView, cardwebinit, CardWebPayinView, BankAccountCreateView, \
    bankaccountdeleteview, TopUpStart

urlpatterns = [
    # path('register/', MangoCardRegistrationView.as_view(), name='cardregistration'),
    path('cardwebinit/', cardwebinit, name='cardwebinit'),
    path('return/', CardWebPayinView.as_view(), name='return'),
    path('bankaccount/create/', BankAccountCreateView.as_view(), name='bankaccountcreate'),
    path('bankaccount/<int:ba_id>/delete/', bankaccountdeleteview, name='bankaccountdelete'),
    path('topup/<uuid:id>/', TopUpStart.as_view(), name='topupstart')
]
