from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .forms import LoginForm, ProductForm
from products.models import Product

# Create your views here.

class AdminLogin(LoginView):
    # テンプレートを選択
    template_name = 'admin/auth/login.html'
    form_class = LoginForm


class AdminLogout(LogoutView):
    # リダイレクトでログインURLに飛ばす
    template_name = 'admin/auth/logout.html'


class AdminProductIndexView(ListView):
    model = Product
    template_name = 'admin/products/index.html'
    context_object_name = "product_list"

    def get_queryset(self):
        return Product.objects.all()


class AdminProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'admin/products/create.html'
    success_url = reverse_lazy('custom_admin:product_index')


class AdminProductDetailView(DetailView):
    model = Product
    template_name = 'admin/products/detail.html'
    context_object_name = 'product_detail'


class AdminProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'admin/products/update.html'
    context_object_name = 'product'
    success_url = reverse_lazy('custom_admin:product_index')


class AdminProductDeleteView(DeleteView):
    model = Product
    template_name = 'admin/products/delete.html'
    context_object_name = 'product'
    success_url = reverse_lazy('custom_admin:product_index')
