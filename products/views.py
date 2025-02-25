from django.shortcuts import render
from django.views import generic
from .models import Product
from cart.models import Cart
from django.views.generic import DetailView

# Create your views here.

class ProductIndexView(generic.ListView):
    model = Product
    template_name = "products/index.html"
    context_object_name = "product_list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = Cart.get_or_create_cart(self.request)
        context["cart_total"] = cart.total_quantity

        return context


class ProductDetailView(generic.DetailView):
    model = Product
    template_name = "products/detail.html"
    context_object_name = "product_detail"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        related_products = Product.objects.order_by("-id")[:4]
        context['related_list'] = related_products

        cart = Cart.get_or_create_cart(self.request)
        context["cart_total"] = cart.total_quantity
        return context
