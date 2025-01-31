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

# Create your views here.
class CartPageView(ListView):
    template_name = 'cart/cart_page.html'
    model = CartProduct

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ECサイトにアクセスしているユーザーのセッションIDを取得
        session_id = self.request.session.session_key
        # なければ強制的にセッションIDを作成
        if not session_id:
            self.request.session.create()
            session_id = self.request.session_session_key
        # セッションIDを元にカートオブジェクトを取得
        cart, created = Cart.objects.get_or_create(session_id=session_id)
        # カートオブジェクトを元にカートない商品を取得
        cart_products = CartProduct.objects.filter(cart=cart)
        # 何種類の商品が追加されたか
        total_type_products = total_cart_products(cart)
        # カート内の全商品の合計金額
        total_cart_amount = sum(cart_product.product.price * cart_product.quantity for cart_product in cart_products)
        # 商品名ごと辞書で格納（デフォルト0に設定）
        product_data = defaultdict(lambda: {"total_price": 0, "quantity": 0})
        # 商品名ごとの合計金額を→オブジェクトリストをfor文で回して
        for cart_product in cart_products:
            product_name = cart_product.product.name
            product_data[product_name]["total_price"] += cart_product.product.price * cart_product.quantity
            product_data[product_name]["id"] = cart_product.id
            product_data[product_name]["price"] = cart_product.product.price
            product_data[product_name]["quantity"] += cart_product.quantity

        context["total_type_products"] = total_type_products
        context["total_cart_amount"] = total_cart_amount
        context["product_data"] = dict(product_data)
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
        # セッションIDを取得（なければ作成）
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session_session_key
        # カートを作成または取得
        cart, created = Cart.objects.get_or_create(session_id=session_id)
        # 商品を取得
        product = get_object_or_404(Product, id=product_id)

        """
        詳細画面から個数指定された際に
        request.POST.get()でname="num"となっているinputタグから取得
        index,reletedはtype="hidden" name="num" value="1" に設定して
        「Add to cart」をクリックした際は value の1を使用
        フォームのデータ型は文字列。整数を扱いたいからint型に変換
        """
        num = request.POST.get("num", "1")
        num = int(num)
        
        # カート内の商品を取得または作成
        # createdは「今回新しく作成された」かどうか（boolean)
        cart_product, created = CartProduct.objects.get_or_create(cart=cart, product=product)
        
        # 今回新しく作成されていない→→既にレコードがある場合
        if not created:
            cart_product.quantity += num
        else:
            # 今回 Add to cartでcart_productテーブルに新しいレコードを追加する場合
            cart_product.quantity = num
        cart_product.save()

        # 合計個数
        cart_total = total_cart_products(cart)

        request.session["cart_total"] = cart_total

        # カート追加時のメッセージ
        messages.success(request, f'{product.name}をカートに追加しました')

        return redirect(request.META.get("HTTP_REFERER", reverse("products:index")))
    
def total_cart_products(cart):
    # 同じカートIDのレコードを取得（filter使用）
    cart_products = CartProduct.objects.filter(cart=cart)

    # 取得したオブジェクトの合計を計算
    total_quantiry = sum(cart_product.quantity for cart_product in cart_products)

    # 合計個数をreturn
    return total_quantiry

class DeleteToCartView(DeleteView):
    template_name = 'cart/delete.html'
    model = CartProduct
    context_object_name = 'cart_product'
    print(context_object_name)
    success_url = reverse_lazy('cart:cart_page')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cart_product = self.get_object()
        context["product_name"] = cart_product.product.name
        context["quantity"] = cart_product.quantity

        return context
