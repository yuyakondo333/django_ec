from django.db import models
from products.models import Product
from django.core.exceptions import ValidationError

# Create your models here.
class Cart(models.Model):
    session_id = models.CharField(max_length=32, unique=True, default="temp_session_id")
    is_purchased = models.BooleanField("購入済み", default=False)

    class Meta:
        db_table = 'cart'

    def __str__(self):
        return f"Cart: {self.id}, Sesson: {self.session_id}"
    
    def check_if_purchased(self, *args, **kwargs):
        if self.is_purchased:
            raise ValidationError("このカートは購入済みのため編集できません")
        super().save(*args, **kwargs)
    
    @classmethod
    def get_or_create_cart(cls, request):
        # セッションIDを取得（なければ作成）
        if not request.session.session_key:
            request.session.create()
        session_id = request.session.session_key

        cart, _ = Cart.objects.get_or_create(session_id=session_id)

        # 購入済みフラグがTrueなら、新しいカートを作成
        if cart.is_purchased:
            request.session.create()    # 新しいセッションを作成
            session_id = request.session.session_key
            cart = Cart.objects.create(session_id=session_id)
            
        return cart
    
    # カート内の合計金額
    @property
    def total_price(self):
        return sum(cart_product.sub_total_price() for cart_product in self.cart_products.all())
    
    # カート内の商品の合計個数
    def total_quantity(self):
        return sum(cart_product.quantity for cart_product in self.cart_products.all())
    
    # カートに商品を追加、個数を増やす（更新）
    def add_product(self, product, quantity):
        cart_product, created = self.cart_products.get_or_create(cart=self, product=product)
        # 今回新しく作成されていない→→既にレコードがある場合
        if not created:
            cart_product.quantity += quantity
        else:
            # 今回 Add to cartでcart_productテーブルに新しいレコードを追加する場合
            cart_product.quantity = quantity
        cart_product.save()
        return cart_product


class CartProduct(models.Model):
    cart = models.ForeignKey("cart.Cart", verbose_name=("カートID"), on_delete=models.CASCADE, related_name="cart_products")
    product = models.ForeignKey("products.Product", verbose_name=("商品ID"), on_delete=models.CASCADE)
    quantity = models.IntegerField(verbose_name='個数', default=1)

    class Meta:
        db_table = 'cart_product'

    def sub_total_price(self):
        return self.product.price * self.quantity
