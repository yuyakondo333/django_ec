from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .forms import LoginForm, ProductForm
from products.models import Product
from order.models import BillingAddress, Order, OrderItem
from django.db.models import Sum

# Create your views here.

class AdminLogin(LoginView):
    # テンプレートを選択
    template_name = 'admin/auth/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('custom_admin:product_index')


class AdminLogout(LogoutView):
    # リダイレクトでログインURLに飛ばす
    template_name = 'admin/auth/logout.html'


class AdminProductIndexView(ListView):
    model = Product
    template_name = 'admin/products/index.html'
    context_object_name = "product_list"

    def get_queryset(self):
        return Product.objects.all().order_by('-id')


class AdminProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'admin/products/create.html'
    success_url = reverse_lazy('custom_admin:product_index')


class AdminProductDetailView(DetailView):
    model = Product
    template_name = 'admin/products/detail.html'
    context_object_name = 'product_detail'


class AdminProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'admin/products/update.html'
    context_object_name = 'product'
    success_url = reverse_lazy('custom_admin:product_index')


class AdminProductDeleteView(DeleteView):
    model = Product
    template_name = 'admin/products/delete.html'
    context_object_name = 'product'
    success_url = reverse_lazy('custom_admin:product_index')


class AdminOrderIndexView(TemplateView):
    template_name = 'admin/order/index.html'

    def get_context_data(self, **kwargs):
        # 親クラスのコンテキストを取得
        context = super().get_context_data(**kwargs)

        # 注文情報を取得(関連情報も取得するためのselect_relatedを使用)
        orders = Order.objects.select_related('billing_address').all().order_by('-id')

        # コンテキストに渡すためのデータを格納するリストを定義
        order_summary = []

        # 各注文に対して、必要な情報を取得
        for order in orders:
            # 同じorder_idを持つOrderItemのsubtotalを合計
            total_subtotal = (
                OrderItem.objects.filter(order=order)
                .aggregate(total=Sum('subtotal'))['total'] or 0
            )

            # 注文ID, 国名, ユーザー名, 合計金額を辞書にしてリストに追加
            order_summary.append({
                "order_id": order.id,
                "country": order.billing_address.country,
                "username": order.billing_address.username,
                "total_price": total_subtotal,
            })

        # コンテキストにorder_summaryを追加
        context["order_summary"] = order_summary

        return context
    

class AdminOrderDetailView(ListView):
    template_name = 'admin/order/detail.html'   # 使用するテンプレートを指定
    context_object_name = 'order_items'  # テンプレートで使用するオブジェクト名を指定

    # クエリセットを取得するメソッドを定義
    def get_queryset(self):
        order_id = self.kwargs.get('pk')    # URLから注文IDを取得
        # order_idに紐づく購入商品を取得し、関連する請求先住所も取得
        return OrderItem.objects.select_related('order__billing_address', 'order__promo_code').filter(order_id=order_id).order_by('-id')
    
    # コンテキストデータを設定するメソッドを定義
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)    # 親クラスのコンテキストを取得

        order_items = self.get_queryset()   # クエリセット(購入商品一覧)を取得
        # 最初の購入商品からユーザー名を取得(購入商品があれば)
        username = order_items[0].order.billing_address.username if order_items else "不明"
        order = order_items[0].order if order_items else None
        discount = order.promo_code.discount if order and order.promo_code.id != 1 else 0

        context['username'] = username  # ユーザー名をコンテキストに追加
        context['order_id'] = self.kwargs.get('pk')     # 注文IDをコンテキストに追加
        context['total_subtotal'] = sum(order_item.subtotal for order_item in order_items)
        context['discount'] = discount

        return context
