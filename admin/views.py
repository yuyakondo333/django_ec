from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .forms import LoginForm
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
    pass


class AdminProductDetailView(DetailView):
    model = Product
    template_name = "admin/products/detail.html"
    context_object_name = "product_detail"


class AdminProductUpdateView(UpdateView):
    pass


class AdminProductDeleteView(DeleteView):
    pass