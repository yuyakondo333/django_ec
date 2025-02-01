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

class CartProduct(models.Model):
    cart = models.ForeignKey("cart.Cart", verbose_name=("カートID"), on_delete=models.CASCADE)
    product = models.ForeignKey("products.Product", verbose_name=("商品ID"), on_delete=models.CASCADE)
    quantity = models.IntegerField(verbose_name='個数', default=1)

    class Meta:
        db_table = 'cart_product'
