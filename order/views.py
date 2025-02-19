from django.shortcuts import render, reverse, redirect
from django.views import View
from cart.models import Cart
from .models import Order, OrderItem
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

        if not cart_products:
            messages.error(request, "カート内に商品がありません")
            return render(request, "cart/cart_page.html", {
                "billing_address_form": billing_address_form,
                "payment_form": payment_form,
            })

        # エラーになった際にカート内の商品情報を保持すための処理
        product_data = {}
        for cart_product in cart_products:
            product_name = cart_product.product.name
            product_data[product_name] = {
                "subtotal": cart_product.sub_total_price(),
                "id": cart_product.id,
                "price": cart_product.product.price,
                "quantity": cart_product.quantity,
            }
        
        # どちらかがエラーの場合、エラーメッセージと共に元の画面へリダイレクト
        if not billing_address_form.is_valid() or not payment_form.is_valid():
            messages.error(request, "入力に間違いがあります")
            return render(request, "cart/cart_page.html", {
                "billing_address_form": billing_address_form,
                "payment_form": payment_form,
                "product_data": product_data,
                "total_cart_price": cart.total_price,
                "total_type_products": len(product_data),
            })
        
        # トランザクション内でDB処理を一括実行
        with transaction.atomic():
            # フォームチェックした請求先住所をDBに保存
            billing_address = billing_address_form.save()
            # フォームチェックした支払い方法をDBに保存
            payment = payment_form.save()
            # 注文情報をDBに保存
            order = Order.objects.create(
                billing_address=billing_address,
                payment=payment
            )
            # カート内の商品をOrderItemテーブルに保存
            for product_name, product_info in product_data.items():
                order_item = OrderItem.objects.create(
                    order=order,
                    name=product_name,
                    price=product_info["price"],
                    quantity=product_info["quantity"],
                    subtotal=product_info["subtotal"]
                )
            # メールを設定していたらメール送信
            if billing_address.email:
                order.send_email(
                    username=billing_address.username,
                    order_id=order.id,
                    order_items=product_data,
                    total_price=sum(item["subtotal"] for item in product_data.values()),
                    email=billing_address.email
                )
            # カートを削除
            Cart.objects.filter(id=cart.id).delete()
        messages.success(request, "ご購入ありがとうございます")

        return redirect(reverse("products:index"))
