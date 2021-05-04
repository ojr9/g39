from django.contrib import admin

from .models import MangoNaturalUser, MangoWallet, MangoCard, MangoLegalUser


@admin.register(MangoNaturalUser)
class MangoNaturalUserAdmin(admin.ModelAdmin):
    list_display = ['id']


@admin.register(MangoCard)
class MangoCardAdmin(admin.ModelAdmin):
    list_display = ['id']


@admin.register(MangoWallet)
class MangoWalletAdmin(admin.ModelAdmin):
    list_display = ['id', 'cuenta']
