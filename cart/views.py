from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.views.generic import TemplateView
from .models import Cart, CartProduct
from products.models import Product

# Create your views here.
class CartPageView(TemplateView):
    template_name = 'cart/cart_page.html'


class AddToCartView(TemplateView):
    def post(self, request, product_id):
        # セッションIDを取得（なければ作成）
        session_id = request.session.session_key
        if not session_id:
            request.session_create()
            session_id = request.session_session_key

        # カートを作成または取得
        cart, created = Cart.objects.get_or_create(session_id=session_id)

        # 商品を取得
        product = get_object_or_404(Product, id=product_id)

        # カート内の商品を取得または作成
        cart_product, created = CartProduct.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_product.quantity += 1
        cart_product.save()

        # カート追加時のメッセージ
        messages.success(request, f'{product.name}をカートに追加しました')

        return redirect(request.META.get("HTTP_REFERER", reverse("products:index")))
