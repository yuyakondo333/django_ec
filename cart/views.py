from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from collections import defaultdict
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import DeleteView
from .models import Cart, CartProduct
from products.models import Product
from .forms import AddToCartForm
from order.forms import BillingAddressForm, PaymentForm
from promotion_code.services.promotion_service import PromotionService
from django.utils.translation import gettext as _

NO_PROMO_CODE = (1, "NOTHING", 0)

# Create your views here.
class CartPageView(ListView):
    template_name = 'cart/cart_page.html'
    model = CartProduct

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # カートオブジェクトを取得
        cart = Cart.get_or_create_cart(self.request)
        # カートオブジェクトを元にカート内の商品を取得
        cart_products = cart.cart_products.select_related("product")

        # PromotionServiceで割引後の価格を取得
        promo_service = PromotionService(self.request)
        total_cart_price, discount = promo_service.get_discounted_total(cart)
        
        # 商品名ごと辞書で格納（デフォルト0に設定）
        product_data = defaultdict(lambda: {"subtotal": 0, "quantity": 0})
        # 商品名ごとの合計金額を→オブジェクトリストをfor文で回して
        for cart_product in cart_products:
            product_name = cart_product.product.name
            product_data[product_name]["subtotal"] += cart_product.sub_total_price()
            product_data[product_name]["id"] = cart_product.id
            product_data[product_name]["price"] = cart_product.product.price
            product_data[product_name]["quantity"] += cart_product.quantity
        
        # セッションに保存されたデータがあれば取得（エラー時のフォームデータ復元）
        billing_address_data = self.request.session.pop("billing_address_form_data", None)
        payment_data = self.request.session.pop("payment_form_data", None)

        # フォームの初期値を設定
        context["billing_address_form"] = BillingAddressForm(initial=billing_address_data if billing_address_data else {})
        context["payment_form"] = PaymentForm(initial=payment_data if payment_data else {})
        context["total_type_products"] = len(cart_products)
        context["total_cart_price"] = total_cart_price
        context["discount"] = discount
        context["promotion_code"] = promo_service.applied_promotion
        context["product_data"] = {
            cart_product.product.name: {
                "subtotal": cart_product.sub_total_price(),
                "id": cart_product.id,
                "price": cart_product.product.price,
                "quantity": cart_product.quantity,
            } for cart_product in cart_products
        }
        return context


class AddToCartView(TemplateView):
    def post(self, request, product_id):
        # フォームでバリデーションチェック
        form = AddToCartForm(request.POST)
        if not form.is_valid():
            messages.error(request, form.errors["num"][0])
            return redirect(request.META.get("HTTP_REFERER", reverse("products:index")))

        # バリデーション済みの値を取得
        num = form.cleaned_data["num"]
        # カートIDを取得
        cart = Cart.get_or_create_cart(self.request)
        # 商品を取得
        product = get_object_or_404(Product, id=product_id)

        """
        詳細画面から個数指定された際にrequest.POST.get()でname="num"となっているinputタグから取得
        index,reletedはtype="hidden" name="num" value="1" に設定して「Add to cart」をクリックした際は value の1を使用
        フォームのデータ型は文字列。整数を扱いたいからint型に変換
        """
        num = int(request.POST.get("num", "1"))
        # カート内の商品を取得または作成
        cart.add_product(product, num)
        # カート追加時のメッセージ
        messages.success(request, f'{product.name}をカートに追加しました')
        # レスポンスで元いたページに戻る
        return redirect(request.META.get("HTTP_REFERER", reverse("products:index")))


class DeleteToCartView(DeleteView):
    template_name = 'cart/product_delete.html'
    model = CartProduct
    context_object_name = 'cart_product'
    success_url = reverse_lazy('cart:cart_page')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cart_product = self.get_object()
        context["product_name"] = cart_product.product.name
        context["quantity"] = cart_product.quantity

        return context


class UseToPromotionCodeView(TemplateView):
    def post(self, request, **kwargs):
        promo_service = PromotionService(request)

        try:
            # プロモーションコードを適用
            promo_service.apply_promotion_code()
            messages.success(request, _("プロモーションコードが適用されました"))
        except ValueError as e:
            messages.error(request, str(e))
        
        return self.redirect_to_cart()
    
    def redirect_to_cart(self):
        return redirect(reverse("cart:cart_page"))


class DeleteToPromotionCodeView(TemplateView):
    template_name = 'cart/promotion_code_delete.html'
    success_url = reverse_lazy('cart:cart_page')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        promotion_code = self.request.session["promotion_code"]
        context["promotion_code"] = promotion_code[1]
        context["discount"] = promotion_code[2]
        return context

    def post(self, request, *args, **kwargs):
        promo_service = PromotionService(request)
        promo_service.remove()
        messages.success(request, _("プロモーションコードを削除しました"))
        return self.redirect_to_cart()

    def redirect_to_cart(self):
        return redirect(reverse("cart:cart_page"))
