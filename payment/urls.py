from django.urls import path

from .views import MangoCardRegistrationView, cardwebinit, CardWebPayinView

urlpatterns = [
    # path('register/', MangoCardRegistrationView.as_view(), name='cardregistration'),
    path('cardwebinit/', cardwebinit, name='cardwebinit'),
    path('return/<int:piid>', CardWebPayinView.as_view(), name='return'),
]
