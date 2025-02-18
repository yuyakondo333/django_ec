from django.db import models
from datetime import datetime
from django.core.validators import MinValueValidator
from django.core.mail import send_mail

# Create your models here.

class BillingAddress(models.Model):
    last_name = models.CharField("姓")
    first_name = models.CharField("名")
    username = models.CharField("ユーザー名", unique=True)
    email = models.EmailField("メールアドレス", blank=True, null=True)
    country = models.CharField("国")
    state_prefecture = models.CharField("州/県")
    zip = models.CharField("郵便番号", max_length=8)
    address1 = models.CharField("住所1", max_length=255)
    address2 = models.CharField("住所2", max_length=255, blank=True, null=True)
    same_address = models.BooleanField("請求先と配送先が同じ", default=False)
    next_save = models.BooleanField("配送先住所を保存", default=False)

    class Meta:
        db_table = 'billing_address'


class Payment(models.Model):
    card_holder = models.CharField("カード名義")
    card_number_hash = models.CharField("カード番号（暗号化）", max_length=255)
    card_last4 = models.CharField("カード下4桁", max_length=19)
    expiration_date = models.CharField("有効期限", max_length=5)

    class Meta:
        db_table = 'payment'

    # ハッシュ化
    @staticmethod
    def hashed_card_number(card):
        import hashlib
        return hashlib.sha256(card.encode()).hexdigest()

    # 下四桁を切り出す
    @staticmethod
    def card_number_slice(card):
        return card[-4:]


class Order(models.Model):
    billing_address = models.ForeignKey("BillingAddress", verbose_name="配送先ID", on_delete=models.CASCADE, related_name="billing_address")
    payment = models.ForeignKey("Payment", verbose_name="支払いID", on_delete=models.CASCADE)
    created_at = models.DateTimeField("購入日時", auto_now_add=True)

    class Meta:
        db_table = 'order'


class OrderItem(models.Model):
    order = models.ForeignKey("Order", verbose_name="注文ID", on_delete=models.CASCADE, related_name="order")
    name = models.CharField("商品名", max_length=20)
    price = models.PositiveIntegerField("商品価格", validators=[MinValueValidator(1)])
    quantity = models.PositiveIntegerField("個数", validators=[MinValueValidator(1)])
    subtotal = models.PositiveIntegerField("小計", validators=[MinValueValidator(1)])

    class Meta:
        db_table = 'order_item'

    # 小計を計算
    def save(self, *args, **kwargs):
        self.subtotal = self.price * self.quantity
        super().save(*args, **kwargs)
