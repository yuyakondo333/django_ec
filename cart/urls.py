from django.urls import path
from . import views

app_name = 'cart'
urlpatterns = [
    path('', views.CartPageView.as_view(), name='cart_page'),
]
