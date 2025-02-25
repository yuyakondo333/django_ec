import re
from django import forms
from django.forms import ModelForm
from .models import BillingAddress, Payment
from django.core.exceptions import ValidationError
from django.utils import timezone

class BillingAddressForm(forms.ModelForm):
    class Meta:
        model = BillingAddress
        fields = ("last_name", "first_name", "username", "email", "country", "state_prefecture",
                "zip", "address1", "address2", "same_address", "next_save"
                )
        
    # last_name, first_name, usernameでアルファベット、かな、カナ、漢字以外でエラー
    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name", "")
        match_word = r'[a-zA-Zぁ-んァ-ン\u4E00-\u9FFF\u3005-\u3007]+'
        re_name = re.compile(match_word)
        if last_name and not re_name.fullmatch(last_name):
            self.add_error("last_name", "姓はアルファベット、ひらがな、カタカナ、漢字で入力してください")
        return last_name
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name", "")
        match_word = r'[a-zA-Zぁ-んァ-ン\u4E00-\u9FFF\u3005-\u3007]+'
        re_name = re.compile(match_word)
        if first_name and not re_name.fullmatch(first_name):
            self.add_error("first_name","名はアルファベット、ひらがな、カタカナ、漢字で入力してください")
        return first_name
    
    def clean_username(self):
        username = self.cleaned_data.get("username", "").strip()
        match_word = r'^[0-9a-zA-Zぁ-んァ-ヶー一-龯々〇〻]+(?:[\s　][0-9a-zA-Zぁ-んァ-ヶー一-龯々〇〻]+)*$'
        re_name = re.compile(match_word)
        if username and not re_name.fullmatch(username):
            self.add_error("username", "ユーザー名は数字、アルファベット、ひらがな、カタカナ、漢字で入力してください")
        return username

    # メールアドレスのチェック
    def clean_email(self, *args, **kwargs):
        # メールアドレスを取得
        email = self.cleaned_data.get("email")

        # 空の場合はそのまま返す
        if not email:
            return email
        
        # 「.com」,「.jp」で終わるメールアドレス以外はエラーを返す
        if not email.endswith((".com", ".jp")):
            self.add_error("email", 'メールアドレスは「.com」「.jp」で終わるメールアドレスにしてください')
        return email

    # 郵便番号のチェック
    def clean_zip(self, *args, **kwargs):
        zip_code = self.cleaned_data.get("zip", "")
        match_word = r'^[0-9]{7}$'
        re_zip = re.compile(match_word)
        if zip_code and not re_zip.fullmatch(zip_code):
            self.add_error("zip", "郵便番号は7桁の数字で入力してください")
        return zip_code


class PaymentForm(forms.ModelForm):
    card_number = forms.CharField(
        label="カード番号",
        max_length=19,
        required=True,
        help_text="クレジットカード番号（ハイフンなしまたは 0000-0000-0000-0000）"
    )

    expiration_date = forms.CharField(
        label="有効期限",
        max_length=5,
        required=True,
        help_text="MM/YY の形式で入力してください"
    )
    
    class Meta:
        model = Payment
        fields = ("card_holder",)

    # クレカ番号のチェック
    def clean_card_number(self, *args, **kwargs):
        # 入力した番号に「-」が含まれている場合は "" にreplace
        card_number = self.cleaned_data.get("card_number").replace("/", "")
        if not card_number:
            self.add_error("card_number", "カード番号を入力してください")
        # 入力内容が数字だけか isdigit() でチェック→数字以外が入っていたらエラー
        if not card_number.isdigit():
            self.add_error("card_number", "カード番号は数字を入力してください")
        # 数字が14~16桁かチェック→それ以外でエラー
        if not (14 <= len(card_number) <= 16):
            self.add_error("card_number", "カード番号は14~16桁で入力してください")
        # Luhnアルゴリズムでカード番号の妥当性をチェック
        if not self.is_luhn_valid(card_number):
            self.add_error("card_number", "無効なカード番号です")
        # バリデーションチェックされたカード番号を返す
        return card_number
        
    # save()で受け取ったカード番号をハッシュ化して下4桁を保存
    def save(self, commit=True):
    # フルカード番号をハッシュ化し、下4桁を保存する
        instance = super().save(commit=False)
        card_number = self.cleaned_data["card_number"]

        instance.card_number_hash = Payment.hashed_card_number(card_number)  # ハッシュ化
        instance.card_last4 = Payment.card_number_slice(card_number)  # 下4桁を保存

        if commit:
            instance.save()
        return instance
    
    # staticmethodでLuhnアルゴリズムを定義
    @staticmethod
    def is_luhn_valid(card_number):
        # 数値を各桁の整数リストに変換する
        def digits_of(n):
            return [int(d) for d in str(n)]
        # カード番号を桁ごとのリストに変換する
        digits = digits_of(card_number)
        # 右端から1桁おき（奇数番目）の数字を抽出する
        odd_digits = digits[-1::-2]
        # 右端から2桁おき（偶数番目）の数字を抽出する
        even_digits = digits[-2::-2]
        # 奇数位置の数字の合計をチェックサムの初期値とする
        checksum = sum(odd_digits)
        # 偶数位置の各数字に対して処理を行う
        for d in even_digits:
            # 2倍した結果を桁ごとのリストに変換し、その合計を求める
            doubled = d * 2
            doubled_digits = digits_of(doubled)
            sum_doubled = sum(doubled_digits)
            checksum += sum_doubled
        return checksum % 10 == 0

    # 有効期限のチェック
    def clean_expiration_date(self, *args, **kwargs):
        # 入力した有効期限を取得して「/」を削除
        expiry = self.cleaned_data.get("expiration_date", "").replace("/", "")
        # 4桁でなければバリデーションエラーを返す
        if len(expiry) != 4 or not expiry.isdigit():
            self.add_error("expiration_date", "有効期限は「MM/YY」の形式で入力してください")
        
        # 1,2文字目を格納 etc:05,11
        expiry_month = int(expiry[:2])
        # 3,4文字目を格納 etc:24,30
        expiry_year = int(expiry[2:])

        # 現在時刻を取得
        current_date = timezone.now()
        # 現在の月を格納
        current_month = current_date.month
        # 現在の西暦を下2桁だけ格納
        current_year = current_date.year % 100

        # 有効期限の月が1~12以外でエラー
        if not (1 <= expiry_month <= 12):
            self.add_error("expiration_date", "有効期限の月が無効です")
        
        # 有効期限の月と現在の月の差が0より小さい and 有効期限の年と現在の年が同じでエラー
        if expiry_month < current_month and expiry_year == current_year:
            self.add_error("expiration_date", "有効期限が切れています")

        # 過去の年はエラー
        if expiry_year < current_year:
            self.add_error("expiration_date", "有効期限が切れています")
        
        # 有効期限の年が未来すぎる場合エラー
        if expiry_year - current_year > 8:
            self.add_error("expiration_date", "有効期限の年が未来すぎです")
        
        # 最後に文字列として返す
        return f"{expiry_month:02}/{expiry_year:02}"
