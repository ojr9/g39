from django.urls import path

from .views import SaverView, SaverUpdate, SaverUpdateMPNU


urlpatterns = [
    path('', SaverView.as_view(), name='saverview'),
    path('update/', SaverUpdate.as_view(), name='saverupdate'),
    path('mupdate/', SaverUpdateMPNU.as_view(), name='savermupdate'),
    # validation should be included in this last link.
]
