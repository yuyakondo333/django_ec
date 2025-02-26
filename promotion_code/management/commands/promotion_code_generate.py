import random, string
from django.core.management.base import BaseCommand
from promotion_code.models import PromotionCode
from django.db import IntegrityError, OperationalError

# 英数字7桁でランダムにプロモーションコードを10個生成
def promotion_code_generate():
    CODE_LENGTH = 7
    NUM_CODES = 10

    chars = string.ascii_letters + string.digits  
    promotion_code_list = [''.join(random.choices(chars, k=CODE_LENGTH)) for _ in range(NUM_CODES)]
    return promotion_code_list

# 各プロモーションコードに割引額を当てはめる ¥100~¥1,000
def generate_discount(promotion_code_list):
    discount_list = list(range(100, 1001, 100))
    discount_dict = {}

    for promotion_code in promotion_code_list:
        discount_dict[promotion_code] = random.choice(discount_list)
    return discount_dict

class Command(BaseCommand):
    help = "custom command : promotion_code_generate"

    def handle(self, *args, **options):
        try:
            promotion_codes = promotion_code_generate()
            discount_mapping = generate_discount(promotion_codes)

            # 作成した{プロモーションコード:割引額}をDBに保存
            for code, discount in discount_mapping.items():
                try:
                    PromotionCode.objects.create(
                        promo_code=code,
                        discount=discount
                    )
                except IntegrityError:
                    error_message = f"プロモーションコード'{code}'が重複しているため、保存できませんでした"
                    self.stderr.write(self.style.ERROR(error_message))

            # コンソールにサクセスメッセージを出力
            self.stdout.write(self.style.SUCCESS("Successfully generated 10 promotion codes!"))

        except OperationalError:
            error_message = "データベースに接続できませんでした"
            self.stderr.write(self.style.ERROR(error_message))

        except Exception as e:
            error_msg = f"不明なエラーが発生しました: {str(e)}"
            self.stderr.write(self.style.ERROR(error_message))
