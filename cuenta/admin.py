from django.contrib import admin
from .models import Cuenta, GoalSaving, GroupSave, LinkPayment, Transaction, Monthlies


@admin.register(Cuenta)
class CuentaAdmin(admin.ModelAdmin):
    list_display = ['id', 'updated', 'user', 'balance', 'currency', 'wid']


@admin.register(GoalSaving)
class GoalSavingAdmin(admin.ModelAdmin):
    list_display = ['id', 'account', 'goal', 'achieved', 'status']


@admin.register(Monthlies)
class MonthliesAdmin(admin.ModelAdmin):
    list_display = ['account', 'date', 'amount', 'status']


@admin.register(GroupSave)
class GroupSaveAdmin(admin.ModelAdmin):
    list_display = ['id', 'account', 'goal', 'achieved', 'status']


@admin.register(LinkPayment)
class LinkPaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'created', 'receiver', 'receiver_account', 'expiry', 'sec_code']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['created', 'type', 'sender', 'receiver', 'amount']

