from django.urls import path

from .views import Index, ToDo, TermsAndConditions

urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('todo/', ToDo.as_view(), name='todo'),
    path('terms-and-conditions/', TermsAndConditions.as_view(), name='terms')
]
