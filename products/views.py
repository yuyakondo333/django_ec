from django.shortcuts import render
from django.views import generic
from .models import Product
from cart.models import Cart
from django.views.generic import DetailView

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

import environ

env = environ.Env()

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

    def get_queryset(self):
        from django.core.mail import send_mail
        from django.core.mail.backends.smtp import EmailBackend
        from sendgrid.helpers.mail import Mail
        from sendgrid import SendGridAPIClient
        import json

        try:
            result = send_mail(
                'Gmailブロック確認テスト',
                'Gmailがこのメールを受信拒否するかテストしています。',
                'buddies3939@ymail.ne.jp',
                ['3939sereson@gmail.com'],
                fail_silently=False,
            )
            print(f"✅ メール送信成功: {result}")
        except Exception as e:
            print(f"🚨 メール送信失敗: {e}")

        # SendGrid APIで直接送信 (レスポンスを詳細表示)
        message = Mail(
            from_email='buddies3939@ymail.ne.jp',
            to_emails='3939sereson@gmail.com',
            subject='Gmail ブロック確認',
            html_content='<strong>Gmailブロック調査用メールです</strong>'
        )

        try:
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(message)
            print(f"📨 ステータスコード: {response.status_code}")
            print(f"📨 レスポンス: {response.body}")
            print(f"📨 ヘッダー: {response.headers}")
        except Exception as e:
            print(f"🚨 SendGridエラー: {str(e)}")


        return Product.objects.all()


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
