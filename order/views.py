from django.shortcuts import render, reverse, redirect
from django.views import View
from django.views.decorators.http import require_POST
from cart.models import Cart, CartProduct
from .models import BillingAddress, Payment, Order
from django.contrib import messages
from django.db import transaction

# Create your views here.
class OrderView(View):
    def post(self, request):
        # 請求先住所のフォームチェック
        # 支払い方法のフォームチェック
        # エラーの場合、リダイレクト
        # 以下は全てelse
        # カートIDを取得、ない場合エラーを返してリダイレクト
        cart = Cart.get_or_create_cart(self.request)
        # カード番号を取得してハッシュ化
        card = request.POST.get("card_number")
        card_number_hashed = Payment.hashed_card_number(card)
        # カード番号の下4桁を切り出す
        card_last4 = Payment.card_number_slice(card)
        # 請求先住所をDBに作成→保存
        # ここから下はトランザクションとして一塊として考える
        with transaction.atomic():
            billing_address = BillingAddress.objects.create(
                last_name = request.POST.get("last_name"),
                first_name = request.POST.get("first_name"),
                username = request.POST.get("username"),
                email = request.POST.get("email"),
                country = request.POST.get("country"),
                state_prefecture = request.POST.get("state_prefecture"),
                zip = request.POST.get("zip"),
                address1 = request.POST.get("address1"),
                address2 = request.POST.get("address2"),
                same_address = request.POST.get("same_address") == "true",
                next_save = request.POST.get("next_save") == "true"
            )

            # 支払い方法をDBに作成→保存
            payment = Payment.objects.create(
                card_holder = request.POST.get("card_holder"),
                card_number_hash = card_number_hashed,
                card_last4 = card_last4,
                expiration_date = request.POST.get("expiration_date"),
            )
            # カートID, 請求先住所, 支払い方法をDBに保存
            order = Order.objects.create(
                cart = cart,
                billing_address = billing_address,
                payment = payment
            )
            # 取得したカートIDからis_purchasedカラムをTrueに変更
            cart.is_purchased = True
            cart.save()
            # 取得したカートIDを持つCartProductを削除
            CartProduct.objects.filter(cart=cart).delete()
            # サクセスメッセージ
            messages.success(request, '購入ありがとうございます')
        # サクセスURLを設定
        return redirect(reverse("products:index"))

