from django import forms

class AddToCartForm(forms.Form):
    num = forms.IntegerField(
        # 負の値を禁止
        min_value=1,
        error_messages={
            "min_value": "個数は1以上を入力してください",
            "invalid" : "整数を入力してください",
        }
    )
