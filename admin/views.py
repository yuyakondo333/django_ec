from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

# Create your views here.

class AdminLoginView():
    pass


class AdminLogoutView():
    pass


class AdminProductIndexView(ListView):
    pass


class AdminProductCreateView(CreateView):
    pass


class AdminProductDetailView(DetailView):
    pass


class AdminProductUpdateView(UpdateView):
    pass


class AdminProductDeleteView(DeleteView):
    pass