from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

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
