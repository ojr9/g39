from django.urls import path

from .views import MangoCardRegistrationView, cardwebinit, CardWebPayinView, BankAccountCreateView, \
    bankaccountdeleteview

urlpatterns = [
    # path('register/', MangoCardRegistrationView.as_view(), name='cardregistration'),
    path('cardwebinit/', cardwebinit, name='cardwebinit'),
    path('return/<int:piid>', CardWebPayinView.as_view(), name='return'),
    path('bankaccount/create/', BankAccountCreateView.as_view(), name='bankaccountcreate'),
    path('bankaccount/<int:ba_id>/delete/', bankaccountdeleteview, name='bankaccountdelete'),
]
