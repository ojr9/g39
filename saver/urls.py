from django.urls import path

from .views import SaverView, SaverUpdate


urlpatterns = [
    path('', SaverView.as_view(), name='saverview'),
    path('update/', SaverUpdate.as_view(), name='saverupdate'),
    # validation should be included in this last link.
]
