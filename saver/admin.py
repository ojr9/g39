from django.contrib import admin

from saver.models import Saver


@admin.register(Saver)
class SaverAdmin(admin.ModelAdmin):
    list_display = ['user', 'mid', 'user_type', 'active', 'validated']

