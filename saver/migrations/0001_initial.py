# Generated by Django 3.2 on 2021-05-06 20:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CorpSaver',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Saver',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('mid', models.PositiveIntegerField(default=0)),
                ('user_type', models.CharField(choices=[('NAT', 'Natural'), ('LEG', 'Legal')], max_length=3)),
                ('active', models.BooleanField(default=True)),
                ('validated', models.BooleanField(default=False)),
                ('birthday', models.DateField(blank=True, null=True)),
                ('nationality', models.CharField(default='DE', max_length=100)),
                ('country_of_residence', models.CharField(default='DE', max_length=100)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='user_saver', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
    ]
