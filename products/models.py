from django.db import models

# Create your models here.

class Product(models.Model):
    class Meta:
        # テーブル名を定義
        db_table = 'product'

    # テーブルのカラムに対応するフィールドを定義
    name = models.CharField(verbose_name='商品名', max_length=255, unique=True)
    price = models.IntegerField(verbose_name='価格', default=0)
    image = models.ImageField(verbose_name='商品画像', max_length=500, null=True, blank=True)
    description = models.TextField(verbose_name='商品説明', max_length=1000)