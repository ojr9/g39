# Generated by Django 3.2.2 on 2021-05-13 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0002_auto_20210510_2208'),
    ]

    operations = [
        migrations.AddField(
            model_name='mangobankaccount',
            name='description',
            field=models.CharField(default='premigration', max_length=25),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='mangobankaccount',
            name='al2',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
