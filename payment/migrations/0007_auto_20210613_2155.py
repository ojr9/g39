# Generated by Django 3.2.4 on 2021-06-13 21:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0006_rename_iban_mangobankaccount_account_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='mangocarddirectpayin',
            name='card',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, related_name='mangodirectpayinscard', to='payment.mangocard'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='mangopayin',
            name='cwid',
            field=models.PositiveIntegerField(default=0),
        ),
    ]