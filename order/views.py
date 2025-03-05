from django.shortcuts import render, reverse, redirect
from django.views import View
from cart.models import Cart
from .models import Order, OrderItem
from .forms import BillingAddressForm, PaymentForm
from django.contrib import messages
from django.db import transaction
from promotion_code.models import PromotionCode
from django.utils import timezone

# Create your views here.
class OrderView(View):
    def post(self, request):
        billing_address_form = BillingAddressForm(request.POST)
        payment_form = PaymentForm(request.POST)
        cart = Cart.get_or_create_cart(self.request)
        cart_products = cart.cart_products.select_related("product")
        # プロモーションコードを取得 なければデフォルト値を格納
        no_promo_code = (1, "NOTHING", 0)
        promotion_code = self.request.session.get("promotion_code", no_promo_code)

        if not cart_products:
            messages.error(request, "カート内に商品がありません")
            return render(request, "cart/cart_page.html", {
                "billing_address_form": billing_address_form,
                "payment_form": payment_form,
            })
        
        error_messages = []
        for field, errors in billing_address_form.errors.items():
            for error in errors:
                error_messages.append(f"{billing_address_form[field].label}: {error}")
        
        for field, errors in payment_form.errors.items():
            for error in errors:
                error_messages.append(f"{payment_form[field].label}: {error}")

        request.session["billing_address_form_data"] = request.POST.dict()
        request.session["payment_form_data"] = request.POST.dict()

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
        if error_messages:
            for message in error_messages:
                messages.error(request, message)

            return redirect(reverse("cart:cart_page"))
        
        # トランザクション内でDB処理を一括実行
        with transaction.atomic():
            # フォームチェックした請求先住所をDBに保存
            billing_address = billing_address_form.save()
            # フォームチェックした支払い方法をDBに保存
            payment = payment_form.save()
            # 注文情報をDBに保存
            order = Order.objects.create(
                billing_address=billing_address,
                payment=payment,
                # プロモーションコードのIDを保存
                promo_code=PromotionCode.objects.get(id=promotion_code[0])
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
            # is_usedカラムをTrue, used_atを購入時刻に更新
            PromotionCode.objects.filter(id=promotion_code[0]).update(
                is_used=True,
                used_at=timezone.now())
            # メールを設定していたらメール送信
            if billing_address.email:
                order.send_email(
                    username=billing_address.username,
                    order_id=order.id,
                    order_items=product_data,
                    # プロモーションコードによる割引額を反映
                    total_price=sum(item["subtotal"] for item in product_data.values()) - promotion_code[2],
                    discount=promotion_code[2],
                    email=billing_address.email
                )
            # 新しいプロモーションコードを1つ作成する
            PromotionCode.create_new_promotion_code()
            # カートを削除
            Cart.objects.filter(id=cart.id).delete()
        messages.success(request, "ご購入ありがとうございます")

        return redirect(reverse("products:index"))
