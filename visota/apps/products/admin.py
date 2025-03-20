from django.contrib import admin, messages
from django.conf import settings
from django.utils.html import format_html
from django.templatetags.static import static
from django.db.models import Prefetch

from django.core.exceptions import ValidationError
from django.utils.translation import get_language

from parler.admin import (
    TranslatableAdmin,
    TranslatableTabularInline,
    TranslatableStackedInline,
    TranslatableBaseInlineFormSet,
)
from django.db import models
from django.forms import HiddenInput, ModelForm
from django import forms
from django.forms.models import BaseInlineFormSet
from .resources import (
    ProductCitySEOExportResource,
    ProductCitySEOImportResource,
    CategoryCitySEOExportResource,
    CategoryCitySEOImportResource,
    TagCitySEOExportResource,
    TagCitySEOImportResource,
)
from import_export.admin import ImportExportMixin
from import_export.formats.base_formats import CSV
from .models import (
    Product,
    Category,
    SubCategory,
    ProductImg,
    ProductDoc,
    CategoryRedirectFrom,
    ProductRedirectFrom,
    Tag,
    TagRedirectFrom,
    ProductCharacteristic,
    Characteristic,
    CharacteristicValue,
)
from .forms import CitySEOExportForm, CitySEOImportForm, CitySEOInlineFormModel, SEOInlineFormModel


class CatalogAbstractAdmin(ImportExportMixin, TranslatableAdmin):
    actions = ("generate_metadata", "generate_city_metadata")
    skip_import_confirm = True
    export_formats = [CSV]
    import_formats = [CSV]
    import_form_class = CitySEOImportForm
    export_form_class = CitySEOExportForm

    def get_export_queryset(self, request):
        return self.model.city_set.through.objects.order_by("entity")
        return super().get_export_queryset(request)

    @admin.action(description="Сгенерировать метаданные")
    def generate_metadata(self, request, qs):
        SEOModel = self.model.seo.related.related_model
        rule = SEOModel.get_default_seo_generation_rule()
        for entity in qs:
            seo = entity.seo
            seo.set_seo_generation_rule(rule)
            for translation in seo.translations.all():
                lang = translation.language_code
                entity.set_current_language(lang)
                title = seo.generate_seo_title_by_entity(entity)
                description = seo.generate_seo_description_by_entity(entity)

                if translation.title == title and translation.description == description:
                    continue

                translation.title = title
                translation.description = description
                translation.save()

        self.message_user(
            request,
            f"Метаданные сгенерированны",
            messages.SUCCESS,
        )

    @admin.action(description="Сгенерировать метаданные по городам")
    def generate_city_metadata(self, request, qs):
        SEOModel = self.model.city_set.through
        rule = SEOModel.get_default_seo_generation_rule()
        full_changes_list = []
        title_changes_list = []
        description_changes_list = []
        qs = qs.prefetch_related(
            Prefetch("city_seo_set", queryset=self.model.city_set.through.objects.select_related("city")),
            "translations",
        )
        for entity in qs:
            for seo in entity.city_seo_set.all():
                lang = seo.city.lang
                entity.set_current_language(lang)
                city = seo.city.name
                seo.set_seo_generation_rule(rule)
                title = seo.generate_seo_title_by_entity(entity, city)
                description = seo.generate_seo_description_by_entity(entity, city)

                if seo.title == title and seo.description == description:
                    continue
                elif seo.title != title and seo.description != description:
                    seo.title = title
                    seo.description = description
                    full_changes_list.append(seo)
                elif seo.title != title and seo.description == description:
                    seo.title = title
                    title_changes_list.append(seo)
                elif seo.title == title and seo.description != description:
                    seo.description = description
                    description_changes_list.append(seo)

        if len(full_changes_list) > 0:
            result = SEOModel.objects.bulk_update(full_changes_list, ["title", "description"])
        if len(title_changes_list) > 0:
            result = SEOModel.objects.bulk_update(title_changes_list, ["title"])
        if len(description_changes_list) > 0:
            result = SEOModel.objects.bulk_update(description_changes_list, ["description"])

        self.message_user(
            request,
            f"Метаданные для городов сгенерированны",
            messages.SUCCESS,
        )

    def get_formset_kwargs(self, request, obj, inline, prefix):
        formset_params = super().get_formset_kwargs(request, obj, inline, prefix)
        lang = request.GET.get("language") or settings.LANGUAGE_CODE

        if isinstance(inline, CitySEOInline):
            formset_params.update(
                {
                    "form_kwargs": [
                        {"city_name": city.name}
                        for city in self.model.city_set.through.city.get_queryset().filter(lang=lang)
                    ],
                }
            )

        if isinstance(inline, CitySEOInline) and (not obj.id or len(obj.name.strip()) == 0):
            formset_params.update(
                {
                    "initial": [
                        {"city": city.id, "header": "", "title": "", "description": ""}
                        for city in self.model.city_set.through.city.get_queryset().filter(lang=lang)
                    ],
                    "form_kwargs": [
                        {"city_name": city.name}
                        for city in self.model.city_set.through.city.get_queryset().filter(lang=lang)
                    ],
                }
            )

        if request.method == "POST":
            data = self._get_data_for_seo_generation(request)
            if isinstance(inline, CitySEOInline):
                formset_params.update(
                    {
                        "form_kwargs": [
                            {
                                "data_for_seo_generation": {"city_name": city.name, **data},
                                "lang": lang,
                                "city_name": city.name,
                            }
                            for city in self.model.city_set.through.city.get_queryset().filter(lang=lang)
                        ]
                    }
                )
            elif isinstance(inline, SEOInline):
                formset_params.update({"form_kwargs": {"data_for_seo_generation": data, "lang": lang}})

        return formset_params

    def get_translation_objects(self, request, language_code, obj=None, inlines=True):
        for o in super().get_translation_objects(request, language_code, obj, inlines):
            yield o
        yield self.model.city_set.through.objects.filter(city__lang=language_code, entity=obj).prefetch_related(
            "city", "entity"
        )

    def _get_data_for_seo_generation(self, request):
        return {"name": request.POST.get("name", "")}

    def get_inlines(self, request, obj):
        lang = request.GET.get("language") or settings.LANGUAGE_CODE
        if obj and lang in obj.get_available_languages():
            return self.inlines + (self.city_seo_inline,)
        return self.inlines

    def save_model(self, request, obj, form, change):
        lang = request.GET.get("language") or settings.LANGUAGE_CODE
        if not change or lang not in obj.get_available_languages():
            self._new_translation_saving = True
        else:
            self._new_translation_saving = False

        return super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        if self._new_translation_saving:
            lang = request.GET.get("language") or settings.LANGUAGE_CODE
            cities = self.model.city_set.rel.related_model.objects.filter(lang=lang)
            self.model.city_set.through.bind_entity_to_cities(form.instance, cities)


class SEOInline(TranslatableStackedInline):
    fieldsets = (
        (None, {"fields": ["title", "description", "noindex_follow"]}),
        (
            "Sitemap",
            {
                "fields": ("change_freq", "priority"),
            },
        ),
    )
    can_delete = False
    form = SEOInlineFormModel
    max_num = 1
    min_num = 1


class CitySEOInlineFormSet(BaseInlineFormSet):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_form_kwargs(self, index):
        if index is None:
            return {}
        if isinstance(self.form_kwargs, list):
            return self.form_kwargs[index]
        return super().get_form_kwargs(index)

    def _existing_object(self, pk):
        return self.model.objects.get(id=pk)


class CitySEOInline(admin.StackedInline):
    formset = CitySEOInlineFormSet
    form = CitySEOInlineFormModel
    can_delete = False
    template = "admin/products/city_seo/stacked.html"
    min_num = 1
    max_num = 1

    def get_formset(self, request, obj=..., **kwargs):
        fs = super().get_formset(request, obj, **kwargs)
        fs.form.base_fields["city"].widget.can_add_related = False
        fs.form.base_fields["city"].widget.can_change_related = False
        fs.form.base_fields["city"].widget.can_view_related = False

        lang = request.GET.get("language") or settings.LANGUAGE_CODE
        fs.form.base_fields["city"].queryset = self.model.city.get_queryset().filter(lang=lang).order_by("name")
        fs.form.base_fields["city"].required = False

        return fs

    def has_delete_permission(self, request, obj=...):
        return False

    def get_queryset(self, request):
        return self.model.objects.none()


class ImgInline(admin.TabularInline):
    model = ProductImg
    min_num = 1
    max_num = 0
    extra = 0
    fields = ("img_url", "order")
    template = "admin/products/product_img/image_inline.html"

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj=None, **kwargs)
        formset.validate_min = True
        return formset

    class Media:
        js = ("products/js/admin/add_img_to_list.js",)


class DocInline(TranslatableTabularInline):
    model = ProductDoc

    def get_queryset(self, request):
        # Limit to a single language!
        language_code = self.get_queryset_language(request)
        return super().get_queryset(request).translated(language_code)


class CharacteristicInline(admin.TabularInline):
    model = ProductCharacteristic

    def get_formset(self, request, obj=None, **kwargs):
        fs = super().get_formset(request, obj, **kwargs)
        fs.form.base_fields["characteristic_value"].widget.can_add_related = False
        fs.form.base_fields["characteristic_value"].widget.can_change_related = False
        fs.form.base_fields["characteristic_value"].widget.can_view_related = False
        # fs.form.base_fields['some_field'].widget.can_delete_related = False

        language_code = get_language()
        fs.form.base_fields["characteristic"].queryset = Characteristic.objects.translated(language_code).order_by(
            "translations__name"
        )

        return fs


class ProductRedirectFromInline(admin.TabularInline):
    model = ProductRedirectFrom
    extra = 1


class CityProductSEOInline(CitySEOInline):
    model = Product.city_set.through

    class Media:
        js = (
            format_html(
                "<script type='module' src='{}'></script>",
                static("products/js/admin/city_seo_inline/city_seo_inline_products.js"),
            ),
        )


class ProductSEOInline(SEOInline):
    model = Product.seo.related.related_model


class ProductAdmin(CatalogAbstractAdmin):
    fields = [
        "name",
        "slug",
        "sub_categories",
        "tags",
        "code",
        "actual_price",
        "current_price",
        "is_present",
        "description",
        "priority",
    ]
    list_display = ["name", "code", "actual_price", "current_price"]
    inlines = (
        CharacteristicInline,
        ImgInline,
        DocInline,
        ProductRedirectFromInline,
        ProductSEOInline,
    )
    city_seo_inline = CityProductSEOInline
    filter_horizontal = (
        "sub_categories",
        "tags",
    )

    def get_export_resource_classes(self, request):
        return [ProductCitySEOExportResource]

    def get_import_resource_classes(self, request):
        return [ProductCitySEOImportResource]

    def _get_data_for_seo_generation(self, request):
        data = super()._get_data_for_seo_generation(request)
        data.update({"price": request.POST.get("current_price", "") or request.POST.get("actual_price", "")})
        return data


class CategoryAdmin(TranslatableAdmin):
    list_display = [
        "name",
    ]
    exclude = ("slug",)

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class CategoryRedirectFromInline(admin.TabularInline):
    model = CategoryRedirectFrom
    extra = 1


class CategorySEOInline(SEOInline):
    model = SubCategory.seo.related.related_model


class CityCategorySEOInline(CitySEOInline):
    model = SubCategory.city_set.through

    class Media:
        js = (
            format_html(
                "<script type='module' src='{}'></script>",
                static("products/js/admin/city_seo_inline/city_seo_inline_categories.js"),
            ),
        )


class SubCategoryAdmin(CatalogAbstractAdmin):
    fields = ["name", "slug", "category", "img", "content", "priority"]
    list_display = ["name", "category"]
    inlines = (
        CategoryRedirectFromInline,
        CategorySEOInline,
    )
    city_seo_inline = CityCategorySEOInline

    def get_export_resource_classes(self, request):
        return [CategoryCitySEOExportResource]

    def get_import_resource_classes(self, request):
        return [CategoryCitySEOImportResource]


class TagRedirectFromInline(admin.TabularInline):
    model = TagRedirectFrom
    extra = 1


class CityTagSEOInline(CitySEOInline):
    model = Tag.city_set.through

    class Media:
        js = (
            format_html(
                "<script type='module' src='{}'></script>",
                static("products/js/admin/city_seo_inline/city_seo_inline_tags.js"),
            ),
        )


class TagSEOInline(SEOInline):
    model = Tag.seo.related.related_model


class TagAdmin(CatalogAbstractAdmin):
    fields = ["name", "slug"]
    list_display = ["name"]
    inlines = (
        TagRedirectFromInline,
        TagSEOInline,
    )
    city_seo_inline = CityTagSEOInline

    def get_export_resource_classes(self, request):
        return [TagCitySEOExportResource]

    def get_import_resource_classes(self, request):
        return [TagCitySEOImportResource]


class CharacteristicValueInlineFormSet(TranslatableBaseInlineFormSet):
    def validate_unique(self):
        name_values = set()
        slug_values = set()
        errors = []
        for form in self.forms:
            name = form["name"].value().strip()
            slug = form["slug"].value().strip()

            if name == "":
                continue

            if name in name_values:
                errors.append("Задано несколько одинаковых значений")
            else:
                name_values.add(name)

            if slug == "":
                continue

            if slug in slug_values:
                errors.append("Задано несколько одинаковых слагов")
            else:
                slug_values.add(slug)

        if errors:
            raise ValidationError(errors)

        return super().validate_unique()


class CharacteristicValueInline(TranslatableTabularInline):
    model = CharacteristicValue
    formset = CharacteristicValueInlineFormSet

    verbose_name = "Возможное значение характеристики"
    verbose_name_plural = "Возможные значения характеристики"


class CharachteristicAdmin(TranslatableAdmin):
    inlines = (CharacteristicValueInline,)

    def get_queryset(self, request):
        language_code = self.get_queryset_language(request)
        return super().get_queryset(request).translated(language_code).order_by("translations__name")


admin.site.register(Characteristic, CharachteristicAdmin)


class CharachteristicValueAdmin(TranslatableAdmin):
    def get_model_perms(self, request):
        return {}


admin.site.register(CharacteristicValue, CharachteristicValueAdmin)


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(Tag, TagAdmin)
