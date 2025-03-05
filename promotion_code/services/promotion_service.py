from promotion_code.models import PromotionCode
from django.utils.translation import gettext as _

NO_PROMO_CODE = (1, "NOTHING", 0)

class PromotionService:
    def __init__(self, request):
        self.request = request
        self.applied_promotion = self.get_promotion_from_session()

    def get_promotion_from_session(self):
        """ セッションからプロモーションコードを取得して、DBからID, 割引額を補完 """
        session_promo = self.request.session.get("promotion_code", NO_PROMO_CODE)

        # セッションのデータ型を統一
        session_promo = tuple(session_promo) if isinstance(session_promo, (list, tuple)) else session_promo

        # セッションに何も保存されていない場合はNO_PROMO_CODEを返す
        if session_promo == NO_PROMO_CODE:
            return NO_PROMO_CODE
        
        # ユーザが入力したプロモーションコードを元にDBから情報を取得
        if isinstance(session_promo, str):
            try:
                promotion = PromotionCode.objects.get(promo_code=session_promo)
                return (promotion.id, promotion.promo_code, promotion.discount)
            # DBに存在しない値だったらNO_PROMO_CODEを返す
            except PromotionCode.DoesNotExist:
                return NO_PROMO_CODE
            
        # 既にプロモーションコードが適用されている場合はそのまま返す (id, promo_code, discount)
        if session_promo != tuple(NO_PROMO_CODE) and isinstance(session_promo, (tuple, list)) and len(session_promo) == 3:
            return session_promo
        
        # 予期しないデータだったらNO_PROMO_CODEを返す
        return NO_PROMO_CODE
    
    @property
    def discount(self):
        """ 割引額を取得 """
        return self.applied_promotion[2]
    
    @property
    def has_applied_promotion(self):
        """ すでに適用済みのプロモーションコードがある場合は True を返す """
        return self.applied_promotion != NO_PROMO_CODE
    
    def apply_promotion_code(self):
        """ ユーザが適用したプロモーションコードを適用 """
        if self.has_applied_promotion:
            raise ValueError(_("すでにプロモーションコードが適用されています"))
        
        promotion_code = self.request.POST.get("promotion_code")
        if not promotion_code:
            raise ValueError(_("プロモーションコードが入力されていません"))
        
        try:
            promotion = PromotionCode.objects.get(promo_code=promotion_code)
        except PromotionCode.DoesNotExist:
            raise ValueError(_("このプロモーションコードは存在しません"))
        
        if promotion.is_used:
            raise ValueError(_("このプロモーションコードは使えません"))
        
        # セッションに(id, promo_code, discount)の形式で保存
        self.request.session["promotion_code"] = (
            promotion.id,
            promotion.promo_code,
            promotion.discount,
        )

    def remove(self):
        """ プロモーションコード削除して初期化 """
        self.request.session["promotion_code"] = NO_PROMO_CODE

    def get_discounted_total(self, cart):
        """ 割引額を適用した合計金額を計算 """
        if self.applied_promotion and self.applied_promotion[1] != NO_PROMO_CODE[1]:
            discount = self.applied_promotion[2]
            total_cart_price = cart.total_price - discount
        else:
            discount = NO_PROMO_CODE[2]
            total_cart_price = cart.total_price
        return total_cart_price, discount
