from django.contrib import admin

from .models import MangoNaturalUser, MangoWallet, MangoCard, MangoLegalUser, MangoBankAccount


@admin.register(MangoNaturalUser)
class MangoNaturalUserAdmin(admin.ModelAdmin):
    list_display = ['id']


@admin.register(MangoCard)
class MangoCardAdmin(admin.ModelAdmin):
    list_display = ['id']


@admin.register(MangoWallet)
class MangoWalletAdmin(admin.ModelAdmin):
    list_display = ['id', 'cuenta']


@admin.register(MangoBankAccount)
class MangoBankAccountAdmin(admin.ModelAdmin):
    list_display = ['id', 'saver', 'bid', 'account_number', 'description']
