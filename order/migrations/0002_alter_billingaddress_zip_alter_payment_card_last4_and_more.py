# Generated by Django 4.2.5 on 2025-02-11 12:41

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billingaddress',
            name='zip',
            field=models.CharField(max_length=8, verbose_name='郵便番号'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='card_last4',
            field=models.CharField(max_length=19, verbose_name='カード下4桁'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='expiration_date',
            field=models.CharField(max_length=5, verbose_name='有効期限'),
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, verbose_name='商品名')),
                ('price', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='商品価格')),
                ('quantity', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='個数')),
                ('subtotal', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='小計')),
                ('order_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order', to='order.order', verbose_name='注文ID')),
            ],
            options={
                'db_table': 'order_item',
            },
        ),
    ]
