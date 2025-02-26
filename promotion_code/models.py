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
