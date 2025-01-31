from django.urls import path
from . import views

app_name = 'cart'
urlpatterns = [
    path('', views.CartPageView.as_view(), name='cart_page'),
    path('add_to_cart/<int:product_id>', views.AddToCartView.as_view(), name='add_to_cart'),
    path('<int:pk>/delete', views.DeleteToCartView.as_view(), name='delete'),
]
