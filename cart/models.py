from django.db import models
from products.models import Product

# Create your models here.
class Cart(models.Model):
    session_id = models.CharField(max_length=32, unique=True)

    class Meta:
        db_table = 'cart'

    def __str__(self):
        return f"Cart: {self.id}, Sesson: {self.session_id}"
    
    @classmethod
    def get_or_create_cart(cls, request):
        # セッションIDを取得（なければ作成）
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        # カートを作成または取得
        cart, created = Cart.objects.get_or_create(session_id=session_id)
        return cart
    
    # カート内の合計金額
    def total_amount(self):
        return sum(cart_product.product.price * cart_product.quantity for cart_product in self.cart_products.all())
    
    # カート内の商品の合計個数
    def total_products(self):
        return sum(cart_product.quantity for cart_product in self.cart_products.all())
    
    # カートに商品を追加、個数を増やす（更新）
    def add_product(self, product, quantity):
        cart_product, created = CartProduct.objects.get_or_create(cart=self, product=product)
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
