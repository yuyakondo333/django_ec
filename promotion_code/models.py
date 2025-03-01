import random, string
from django.db import models
from django.utils import timezone

# Create your models here.
class PromotionCode(models.Model):
    promo_code = models.CharField("プロモーションコード", max_length=7, unique=True)
    discount = models.IntegerField("割引額")
    is_used = models.BooleanField("使用済み判定", default=False)
    used_at = models.DateTimeField("使用日時", default=timezone.now)

    class Meta:
        db_table = 'promotion_code'

    def __str__(self):
        return f"{self.promo_code} : {self.discount}"
    
    # 新しいプロモーションコードを1つ作成
    @classmethod
    def new_promotion_code(cls):
        CODE_LENGTH = 7
        chars = string.ascii_letters + string.digits
        promotion_code = ''.join(random.choices(chars, k=CODE_LENGTH))
        return promotion_code
    
    # プロモーションコードに対応する割引額を作成
    @classmethod
    def new_discount(cls):
        discount_list = list(range(100, 1001, 100))
        new_discount = random.choice(discount_list)
        return new_discount
    
    @classmethod
    def create_new_promotion_code(cls):
        promotion_code = cls.new_promotion_code()
        discount = cls.new_discount()

        new_promo = cls.objects.create(
            promo_code=promotion_code,
            discount=discount
        )

        return new_promo
