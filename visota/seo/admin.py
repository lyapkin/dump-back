from typing import Any
from django.contrib import admin
from django.http import HttpRequest
from parler.admin import TranslatableAdmin, TranslatableTabularInline
from .models import *


# Register your models here.
class RobotsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Robots, RobotsAdmin)


class SEOStaticPageAdmin(TranslatableAdmin):
    ordering = ("order",)

    def get_fieldsets(self, request, obj=None):
        if obj:
            return (
                (None, {"fields": ["name", "header", "title", "description", "noindex_follow", "order"]}),
                (
                    "Sitemap",
                    {
                        "fields": ("change_freq", "priority"),
                    },
                ),
            )
        else:
            return (
                (None, {"fields": ["page", "name", "header", "title", "description", "noindex_follow", "order"]}),
                (
                    "Sitemap",
                    {
                        "fields": ("change_freq", "priority"),
                    },
                ),
            )

    # def get_fields(self, request, obj=None):
    #   if obj:
    #       return ['name', 'header', 'title', 'description', 'noindex_follow', 'order', 'change_freq', 'priority']
    #   else:
    #       return ['page', 'name', 'header', 'title', 'description', 'noindex_follow', 'order', 'change_freq', 'priority']

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["name"]
        else:
            return []

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(SEOStaticPage, SEOStaticPageAdmin)


class SEOCategoryPageAdmin(TranslatableAdmin):
    fieldsets = (
        (None, {"fields": ["category", "title", "description", "noindex_follow"]}),
        (
            "Sitemap",
            {
                "fields": ("change_freq", "priority"),
            },
        ),
    )
    actions = ["generate_meta"]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=...):
        if request.get_full_path_info().split("/")[2] == "products":
            return True
        return False

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["category"]
        else:
            return []

    @admin.action(description="Сгенерировать метаданные")
    def generate_meta(self, request, queryset):
        rule = MetaGenerationRule.objects.get(type="ctg")
        for seo in queryset:
            category = seo.category
            for translation in category.translations.all():
                if rule.has_translation(translation.language_code):
                    rule.set_current_language(translation.language_code)
                    title = rule.title.format(name=translation.name, description=translation.description)
                    description = rule.description.format(name=translation.name, description=translation.description)
                else:
                    title = translation.name
                    description = translation.description
                seo.set_current_language(translation.language_code)
                seo.title = title
                seo.description = description
            seo.save()


admin.site.register(SEOCategoryPage, SEOCategoryPageAdmin)


class SEOTagPageAdmin(TranslatableAdmin):
    fieldsets = (
        (None, {"fields": ["tag", "title", "description", "noindex_follow"]}),
        (
            "Sitemap",
            {
                "fields": ("change_freq", "priority"),
            },
        ),
    )
    actions = ["generate_meta"]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=...):
        if request.get_full_path_info().split("/")[2] == "products":
            return True
        return False

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["tag"]
        else:
            return []

    @admin.action(description="Сгенерировать метаданные")
    def generate_meta(self, request, queryset):
        rule = MetaGenerationRule.objects.get(type="tag")
        for seo in queryset:
            tag = seo.tag
            for translation in tag.translations.all():
                if rule.has_translation(translation.language_code):
                    rule.set_current_language(translation.language_code)
                    title = rule.title.format(name=translation.name)
                    description = rule.description.format(name=translation.name)
                else:
                    title = translation.name
                    description = translation.name
                seo.set_current_language(translation.language_code)
                seo.title = title
                seo.description = description
            seo.save()


admin.site.register(SEOTagPage, SEOTagPageAdmin)


class SEOProductPageAdmin(TranslatableAdmin):
    fieldsets = (
        (None, {"fields": ["product", "title", "description", "noindex_follow"]}),
        (
            "Sitemap",
            {
                "fields": ("change_freq", "priority"),
            },
        ),
    )
    actions = ["generate_meta"]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=...):
        if request.get_full_path_info().split("/")[2] == "products":
            return True
        return False

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["product"]
        else:
            return []

    @admin.action(description="Сгенерировать метаданные")
    def generate_meta(self, request, queryset):
        rule = MetaGenerationRule.objects.get(type="prd")
        for seo in queryset:
            product = seo.product
            for translation in product.translations.all():
                lang = translation.language_code
                if rule.has_translation(lang):
                    rule.set_current_language(lang)

                    price = product.current_price or product.actual_price or ""
                    cats_q = product.sub_categories.language(lang).filter(translations__language_code=lang)
                    cats = ", ".join([c.name for c in cats_q])
                    chars_q = product.productcharacteristic_set.all()
                    chars = []
                    for char in chars_q:
                        char_key = char.characteristic
                        char_value = char.characteristic_value
                        char_key.set_current_language(lang)
                        char_value.set_current_language(lang)
                        chars.append("{} - {}".format(char_key.name, char_value.name))
                    chars = "; ".join(chars)

                    title = rule.title.format(name=translation.name, price=price, cats=cats, chars=chars)
                    description = rule.description.format(name=translation.name, price=price, cats=cats, chars=chars)
                else:
                    title = translation.name
                    description = translation.name
                seo.set_current_language(lang)
                seo.title = title
                seo.description = description
            seo.save()


admin.site.register(SEOProductPage, SEOProductPageAdmin)


class SEOPostPageAdmin(TranslatableAdmin):
    fieldsets = (
        (None, {"fields": ["post", "title", "description", "noindex_follow"]}),
        (
            "Sitemap",
            {
                "fields": ("change_freq", "priority"),
            },
        ),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["post"]
        else:
            return []


admin.site.register(SEOPostPage, SEOPostPageAdmin)


class MetaGenerationRuleAdmin(TranslatableAdmin):
    fields = ["type", "instruction", "title", "description"]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["type", "instruction"]
        else:
            return []

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(MetaGenerationRule, MetaGenerationRuleAdmin)


class JSFileAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["name"]
        else:
            return []

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(JSFile, JSFileAdmin)


class CSSFileAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["name"]
        else:
            return []

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(CSSFile, CSSFileAdmin)


# class RedirectAdmin(admin.ModelAdmin):
#     fields = ("src", "to", "permanent")
#     list_display = ("src", "to", "permanent")


class RedirectInline(TranslatableTabularInline):
    model = Redirect
    fields = ("src", "to")
    template = "admin/redirects/redirect_inline.html"

    def get_queryset(self, request):
        # Limit to a single language!
        language_code = self.get_queryset_language(request)
        return super().get_queryset(request).translated(language_code)


class GhostRedirectAdmin(TranslatableAdmin):
    inlines = (RedirectInline,)

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(GhostRedirect, GhostRedirectAdmin)


class CityAdmin(admin.ModelAdmin):
    exclude = ("sitemap",)

    def get_readonly_fields(self, request, obj=...):
        if obj:
            return ("lang",)
        return super().get_readonly_fields(request, obj)

    def save_model(self, request, city, form, change):
        super().save_model(request, city, form, change)

        if not change:
            self._bind_city_to_entity(city, Product, city.products.through)
            self._bind_city_to_entity(city, SubCategory, city.categories.through)
            self._bind_city_to_entity(city, Tag, city.tags.through)

    def _bind_city_to_entity(self, city, EntityClass, M2mClass):
        rule = M2mClass.get_default_seo_generation_rule()
        lang = city.lang
        entities = EntityClass.objects.filter(translations__language_code=lang)
        city_entity_list = []
        for e in entities:
            e.set_current_language(lang)
            seo = M2mClass(city=city, entity=e, header=e.name)
            seo.set_seo_generation_rule(rule)
            seo.title = seo.generate_seo_title_by_entity(e, city.name)
            seo.description = seo.generate_seo_description_by_entity(e, city.name)
            city_entity_list.append(seo)

        M2mClass.objects.bulk_create(city_entity_list)


admin.site.register(City, CityAdmin)
