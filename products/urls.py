from django.urls import path
from . import views

app_name = 'products'
urlpatterns = [
    path('', views.ProductIndexView.as_view(), name='index'),
    path('<int:pk>/',views.ProductDetailView.as_view(),name='detail'),
]