from django.urls import path

from .views import LoanIndex


urlpatterns = [
    path('', LoanIndex.as_view(), name='loansindex'),
]
