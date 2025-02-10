from django.shortcuts import render, reverse, redirect
from django.views import View
from django.views.decorators.http import require_POST
from cart.models import Cart, CartProduct
from .models import BillingAddress, Payment, Order
from .forms import BillingAddressForm, PaymentForm
from django.contrib import messages
from django.db import transaction

# Create your views here.
class OrderView(View):
    def post(self, request):
        # 請求先住所フォームと支払いフォームを生成
        billing_address_form = BillingAddressForm(request.POST)
        payment_form = PaymentForm(request.POST)
        # カートIDを取得、ない場合エラーを返してリダイレクト
        cart = Cart.get_or_create_cart(self.request)
        cart_products = cart.cart_products.select_related("product")

        product_data = {}
        for cart_product in cart_products:
            product_name = cart_product.product.name
            product_data[product_name] = {
                "total_price": cart_product.sub_total_price(),
                "id": cart_product.id,
                "price": cart_product.product.price,
                "quantity": cart_product.quantity,
            }
        
        # どちらかがエラーの場合、エラーメッセージと共に元の画面へリダイレクト
        if not billing_address_form.is_valid() or not payment_form.is_valid():
        # if not billing_address_form.is_valid():
            messages.error(request, "エラーっすよ、あかんっすよ")
            print("billing_address_form.is_valid():", billing_address_form.is_valid())
            print("payment_form.is_valid():", payment_form.is_valid())
            return render(request, "cart/cart_page.html", {
                "billing_address_form": billing_address_form,
                "payment_form": payment_form,
                "product_data": product_data,
                "total_cart_price": cart.total_price,
                "total_type_products": len(product_data),
            })
        
        # カート内の商品がない場合エラーを返してリダイレクト
        if not cart_products:
            raise ValueError("カート内に商品がありません")
        
        # トランザクション内でDB処理を一括実行
        with transaction.atomic():
            # フォームチェックした請求先住所をDBに保存
            billing_address = billing_address_form.save()
            # フォームチェックした支払い方法をDBに保存
            payment = payment_form.save()
            # 注文情報をDBに保存
            order = Order.objects.create(
                cart=cart,
                billing_address=billing_address,
                payment=payment
            )
            # カート購入フラグを更新
            cart.is_purchased = True
            cart.save()
            # カート内の商品を削除
            CartProduct.objects.filter(cart=cart).delete()
            messages.success(request, "ご購入ありがとうございます")
            print("購入したよ")

        return redirect(reverse("products:index"))
