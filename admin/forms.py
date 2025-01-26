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


class ProductRegisterForm(ModelForm):
    # 商品登録画面用のフォーム
    class Meta:
        # 利用するモデルクラスを指定
        model = Product
        # 利用するモデルのフィールドを指定
        fields = '__all__'  # モデルの全フィールドを使用
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '商品名を入力してください'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '価格を入力してください'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': '商品説明を入力してください'}),
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise ValidationError("商品名を入力してください。")
        return name