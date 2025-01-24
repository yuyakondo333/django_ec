from django.urls import include, path
from . import views

app_name = 'admin'

urlpatterns = [
    # 管理画面の商品に関するURL
    path('products/', views.AdminProductIndexView.as_view(), name='product_index'),
    path('products/<int:pk>/',views.AdminProductDetailView.as_view(),name='product_detail'),
    path('products/<int:pk>/edit',views.AdminProductEditView.as_view(),name='product_edit'),
    path('products/<int:pk>/update',views.AdminProductUpdateView.as_view(),name='product_update'),
    path('products/<int:pk>/delete',views.AdminProductDeleteView.as_view(),name='product_delete'),

    # 管理画面のログイン、ログアウトに関するURL
    path('login',views.AdminLoginView.as_view(),name='login'),
    path('logout',views.AdminLogoutView.as_view(),name='logout'),
]