# Generated by Django 3.2.4 on 2021-06-13 21:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cuenta', '0007_auto_20210608_2152'),
    ]

    operations = [
        migrations.AlterField(
            model_name='linkpayment',
            name='sec_code',
            field=models.PositiveSmallIntegerField(default=15324, editable=False),
        ),
    ]
