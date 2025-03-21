# Generated by Django 3.2.7 on 2024-11-16 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0008_delete_shippingaddress'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('credit_card', 'Credit Card'), ('debit_card', 'Debit Card'), ('net_banking', 'Net Banking'), ('cash_on_delivery', 'Cash on Delivery')], default='credit_card', max_length=50),
            preserve_default=False,
        ),
    ]
