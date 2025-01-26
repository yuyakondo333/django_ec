from django.db import models

# Create your models here.

class Product(models.Model):
    class Meta:
        # テーブル名を定義
        db_table = 'product'
        # モデル名の日本語化 /adminのサイドバーの出力
        verbose_name = '商品'
        # 表示の乱れをなくす
        verbose_name_plural = '商品'

    # テーブルのカラムに対応するフィールドを定義
    name = models.CharField(verbose_name='商品名', max_length=255, unique=True)
    price = models.IntegerField(verbose_name='価格', default=0)
    image = models.ImageField(verbose_name='商品画像', null=True, blank=True)
    description = models.TextField(verbose_name='商品説明', max_length=1000)

    # admin画面の表示内容
    def __str__(self):
        return self.name