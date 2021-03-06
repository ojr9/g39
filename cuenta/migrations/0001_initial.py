# Generated by Django 3.2 on 2021-05-06 20:09

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('saver', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cuenta',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(db_index=True, default=uuid.uuid4, editable=False, max_length=35, primary_key=True, serialize=False)),
                ('activation', models.BooleanField(default=True)),
                ('viban', models.CharField(max_length=35, null=True)),
                ('currency', models.CharField(choices=[('EUR', 'Euro'), ('USD', 'USD'), ('CHF', 'Swiss Franc')], default='EUR', max_length=3)),
                ('balance', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('wid', models.IntegerField(default=0, verbose_name='Wallet ID')),
                ('description', models.CharField(max_length=200)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=7, validators=[django.core.validators.MinValueValidator(50, message='50 is the minimum value here')])),
                ('description', models.CharField(blank=True, max_length=150, null=True)),
                ('type', models.CharField(choices=[('TopUoooop', 'TopUphahah  '), ('Donation', 'Donation'), ('LinkPayment', 'LinkPayment'), ('ToGoal', 'Added to Goal')], max_length=11)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='receiver-user+', to=settings.AUTH_USER_MODEL)),
                ('receiver_account', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='receiver-account+', to='cuenta.cuenta')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='sender-user+', to=settings.AUTH_USER_MODEL)),
                ('sender_account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='sender-account+', to='cuenta.cuenta')),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='LinkPayment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('WAIT', 'Awaiting Payment'), ('PAID', 'Payment Successful'), ('CANC', 'Link Cancelled'), ('EXPR', 'Link Expired')], default='WAIT', max_length=4)),
                ('expiry', models.DurationField(editable=False)),
                ('description', models.CharField(max_length=35)),
                ('execution', models.DateTimeField(blank=True, null=True)),
                ('amount', models.DecimalField(decimal_places=2, default=0.01, max_digits=8, validators=[django.core.validators.MinValueValidator(0.01)])),
                ('sec_code', models.PositiveSmallIntegerField(default=60030, editable=False)),
                ('qr_link', models.ImageField(null=True, upload_to='static/qr_links/')),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receiverForLink', to='saver.saver')),
                ('receiver_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receiverAccount', to='cuenta.cuenta')),
                ('sender', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sender', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='GroupSave',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=250)),
                ('description', models.TextField(blank=True, help_text='Add a description if you like, here', null=True)),
                ('goal', models.IntegerField(validators=[django.core.validators.MinValueValidator(250, message='Minimum amount is 250.')])),
                ('achieved', models.DecimalField(decimal_places=2, default=0.0, max_digits=5)),
                ('monthly', models.DecimalField(decimal_places=2, max_digits=8)),
                ('status', models.CharField(choices=[('CREA', 'CREATED'), ('PROG', 'IN PROGRESS'), ('ACCO', 'ACCOMPLISHED'), ('TERM', 'TERMINATED')], default='CREA', max_length=4)),
                ('image', models.ImageField(blank=True, null=True, upload_to='images/goals/')),
                ('video', models.URLField(blank=True, null=True)),
                ('account', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='cuenta.cuenta')),
                ('members', models.ManyToManyField(related_name='_cuenta_groupsave_members_+', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='GoalSaving',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=25)),
                ('description', models.TextField(blank=True, help_text='Add a description if you like, here', null=True)),
                ('goal', models.IntegerField(validators=[django.core.validators.MinValueValidator(250, message='Minimum amount is 250.')])),
                ('achieved', models.DecimalField(decimal_places=2, default=0.0, max_digits=5)),
                ('monthly', models.DecimalField(decimal_places=2, default=0.0, help_text='Want to add a monthly topup amount? Leave at 0 if not.', max_digits=8, null=True)),
                ('status', models.CharField(choices=[('CREA', 'CREATED'), ('PROG', 'IN PROGRESS'), ('ACCO', 'ACCOMPLISHED'), ('TERM', 'TERMINATED')], default='CREA', max_length=4)),
                ('image', models.ImageField(blank=True, null=True, upload_to='images/goals/')),
                ('video', models.URLField(blank=True, null=True)),
                ('duration', models.DurationField()),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cuenta.cuenta')),
            ],
        ),
    ]
