from django.contrib import admin
from django import forms

from .models import *


class ConsultationRequestAdmin(admin.ModelAdmin):
    list_display = ["name", "number", "date"]


class OfferRequestAdmin(admin.ModelAdmin):
    list_display = ["name", "number", "date"]


class PriceRequestAdmin(admin.ModelAdmin):
    list_display = ["name", "number", "date"]


class ProductsInline(admin.TabularInline):
    model = ProductOrder
    min_num = 1

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj=None, **kwargs)
        formset.validate_min = True
        return formset


# class OrderForm(forms.ModelForm):
#     # charachteristics = forms.ModelMultipleChoiceField(queryset=CharValue.objects.order_by('char__name'))
#     # sub_categories = forms.ModelMultipleChoiceField(queryset=SubCategory.objects.order_by('name'))

#     class Meta:
#         model = Product
#         fields = '__all__'

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['charachteristics'].queryset = (
#             self.fields['charachteristics'].queryset.order_by('char__name')
#         )
#         self.fields['sub_categories'].queryset = (
#             self.fields['sub_categories'].queryset.order_by('name')
#         )


class OrderAdmin(admin.ModelAdmin):
    list_display = ["name", "number", "date"]
    inlines = [ProductsInline]


class SampleRequestAdmin(admin.ModelAdmin):
    list_display = ["name", "number", "date"]


admin.site.register(ConsultationRequest, ConsultationRequestAdmin)
admin.site.register(CommercialOfferRequest, OfferRequestAdmin)
admin.site.register(PriceRequest, PriceRequestAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(SampleRequest, SampleRequestAdmin)
