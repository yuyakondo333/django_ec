from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.views.generic import TemplateView
from .models import Cart, CartProduct
from products.models import Product
from .forms import AddToCartForm

# Create your views here.
class CartPageView(TemplateView):
    template_name = 'cart/cart_page.html'


class AddToCartView(TemplateView):
    def post(self, request, product_id):
        form = AddToCartForm(request.POST)
        if not form.is_valid():
            messages.error(request, form.errors["num"][0])  # エラーメッセージを表示
            return redirect(request.META.get("HTTP_REFERER", reverse("products:index")))

        num = form.cleaned_data["num"]  # ✅ バリデーション済みの値を取得
        # セッションIDを取得（なければ作成）
        session_id = request.session.session_key
        if not session_id:
            request.session_create()
            session_id = request.session_session_key

        # カートを作成または取得
        cart, created = Cart.objects.get_or_create(session_id=session_id)

        # 商品を取得
        product = get_object_or_404(Product, id=product_id)

        """
        詳細画面から個数指定された際に
        request.POST.get()でname="num"となっているinputタグから取得
        「Add to cart」をクリックした際はデフォルトの1を使用
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
