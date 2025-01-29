from django.db import models
from products.models import Product

# Create your models here.
class Cart(models.Model):
    session_id = models.CharField(max_length=32, unique=True, null=True, blank=True)

    class Meta:
        db_table = 'cart'

    def __str__(self):
        return f"Cart: {self.id}, Sesson: {self.session_id}"
    

class CartProduct(models.Model):
    cart = models.ForeignKey("cart.Cart", verbose_name=("カートID"), on_delete=models.CASCADE)
    product = models.ForeignKey("products.Product", verbose_name=("商品ID"), on_delete=models.CASCADE)
    quantity = models.IntegerField(verbose_name='個数', default=1)

    class Meta:
        db_table = 'cart_product'
