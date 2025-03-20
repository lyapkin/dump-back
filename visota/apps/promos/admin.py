from django.contrib import admin
from django import forms

from .models import Promo, Bonus

# Register your models here.

# class PromoAdmin(admin.ModelAdmin):
#     list_display = ["title", 'is_active', 'last_day']
#     ordering=['-last_day']


# # class BonusAdmin(admin.ModelAdmin):
# #     list_display = ['condition']


# admin.site.register(Promo, PromoAdmin)
# admin.site.register([Bonus])