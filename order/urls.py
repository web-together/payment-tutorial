from django.urls import path
from .views import *

app_name = 'order'

urlpatterns = [
    path('', index, name='index'),
    path('payment', payment, name='payment'),
]