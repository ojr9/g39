from django.urls import path
from .views import CuentaCreate, CuentaDelete, CuentaView, CuentaList, GoalSavingCreate, GoalSavingDetail,\
    GoalSavingUpdate, GoalSavingAbort, deposit, PaymentLinkCreate, LinkView,\
    PaymentLinkList, PaymentLinkListView, savetogoal, cancellink, LinkSendPreV, Payout
from payment.views import MangoCardRegistrationView, ibanize, MangoCardPreRegistrationView

# If errors happen make sure to clean up the ORDER of links
urlpatterns = [
    # Cuenta
    path('create/', CuentaCreate.as_view(), name='cuentacreate'),
    path('<uuid:id>/', CuentaView.as_view(), name='cuentaview'),
    path('<uuid:id>/<int:goal_id>/', GoalSavingDetail.as_view(), name='goalsaveview'),
    path('<uuid:id>/<int:goal_id>/save/', savetogoal, name='savetogoal'),
    path('<uuid:id>/<int:goal_id>/update/', GoalSavingUpdate.as_view(), name='goalsaveupdate'),
    path('<uuid:id>/<int:goal_id>/abort/', GoalSavingAbort.as_view(), name='goalsaveabort'),
    path('<uuid:id>/close/', CuentaDelete.as_view(), name='cuentadelete'),
    path('<uuid:id>/deposit/', deposit, name='deposit'),
    path('<uuid:id>/card-register/', MangoCardPreRegistrationView.as_view(), name='cardregistration'),
    path('<uuid:id>/ibanize/', ibanize, name='ibanize'),
    path('<uuid:id>/createsavingsgoal/', GoalSavingCreate.as_view(), name='goalsavecreate'),
    path('<uuid:id>/createlink/', PaymentLinkCreate.as_view(), name='linkcreate'),
    path('<uuid:id>/accountlinks/', PaymentLinkListView.as_view(), name='linklist'),
    path('<uuid:id>/withdraw/', Payout.as_view(), name='payout'),
    path('<int:pl_id>/', LinkView.as_view(), name='linkview'),
    path('<int:pl_id>/prev/', LinkSendPreV.as_view(), name='linksendpreview'),
    path('<int:pl_id>/cancel/', cancellink, name='linkcancel'),
    path('links/list/', PaymentLinkList.as_view(), name='linklistall'),
    path('', CuentaList.as_view(), name='cuentalist')
]
