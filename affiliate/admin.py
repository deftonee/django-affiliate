# -*- coding: utf-8 -*-
from django.apps import apps
from django.contrib import admin
from . import app_settings

Affiliate = apps.get_model(app_settings.AFFILIATE_MODEL)


class AffiliateAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'is_active', 'reward_amount',
                    'reward_percentage', 'created_at')
    raw_id_fields = ('user',)


admin.site.register(Affiliate, AffiliateAdmin)
