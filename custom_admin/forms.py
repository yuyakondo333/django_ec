from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from products.models import Product

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            # 全てのフォームの部品のclass属性に「form-control」を指定（bootstrapのフォームデザインを利用するため）
            field.widget.attrs['class'] = 'form-control'
            # 全てのフォームの部品にpaceholderを定義して、入力フォームにフォーム名が表示されるように指定。
            field.widget.attrs['placeholder'] = field.label

    # username, password両方合わせたバリデーションチェック
    def clean(self):
        clean_data = super().clean()
        username = clean_data.get('username')
        password = clean_data.get('password')

        # ユーザー名またはパスワードが空の場合のバリデーション
        if not username or not password:
            raise ValidationError("ユーザー名とパスワードを入力してください")
        
        return clean_data


class ProductForm(ModelForm):
    # 商品登録画面用のフォーム
    class Meta:
        # 利用するモデルクラスを指定
        model = Product
        # 利用するモデルの全フィールドを指定
        fields = ['name', 'price', 'image', 'description']

    def clean_name(self):
        name = self.cleaned_data.get('name')
        # nameが空だったらバリデーションエラー
        if not name:
            raise ValidationError("商品名を入力してください。")
        # nameが256文字以上だったらバリデーションエラー
        if len(name) > 255:
            raise ValidationError("商品名は255文字以内にしてください")
        return name
    
    def clean_price(self):
        price = self.cleaned_data.get('price')
        # priceが空だったらバリデーションエラー
        if not price:
            raise ValidationError("価格を入力してください。")
        # priceが0以下、int型以外だったらバリデーションエラー
        if price < 0 or type(price) != int:
            raise ValidationError("価格は1以上の整数を入力してください")
        return price
    
    def clean_description(self):
        description = self.cleaned_data.get('description')
        # descriptionが空だったらバリデーションエラー
        if not description:
            raise ValidationError("商品名を入力してください。")
        # descriptionが1001文字以上だったらバリデーションエラー
        if len(description) > 1000:
            raise ValidationError("商品説明は1000文字以内にしてください")
        return description
    
    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        price = cleaned_data.get('price')
        return cleaned_data