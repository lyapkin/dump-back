from django.contrib import admin

from .models import *


# Register your models here.
class VacancyAdmin(admin.ModelAdmin):
    list_display = ["name", 'last_modified', 'is_open']
    prepopulated_fields = {"slug": ("name",)}
    ordering=['-last_modified']



admin.site.register(Vacancy, VacancyAdmin)