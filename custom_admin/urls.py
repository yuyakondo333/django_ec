from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views

app_name = 'custom_admin'

urlpatterns = [
    # 管理画面のログイン、ログアウトに関するURL
    path('login/',views.AdminLogin.as_view(),name='login'),
    path('logout/',login_required(views.AdminLogout.as_view()),name='logout'),
    
    # 管理画面の商品に関するURL
    path('products/', login_required(views.AdminProductIndexView.as_view()), name='product_index'),
    path('products/create', login_required(views.AdminProductCreateView.as_view()), name='product_create'),
    path('products/<int:pk>/',login_required(views.AdminProductDetailView.as_view()),name='product_detail'),
    path('products/<int:pk>/update',login_required(views.AdminProductUpdateView.as_view()),name='product_update'),
    path('products/<int:pk>/delete',login_required(views.AdminProductDeleteView.as_view()),name='product_delete'),
]