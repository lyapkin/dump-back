from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, CharWidget
from .models import Product, SubCategory, Tag


class PageDescriptionFieldMixin(resources.ModelResource):
    page_description = fields.Field(
        column_name="текстовое описание",
        attribute="page_description",
    )


class CitySEOExportResource(resources.ModelResource):
    city = fields.Field(column_name="город", attribute="city", widget=ForeignKeyWidget(Product, field="name"))

    class Meta:
        fields = (
            "id",
            "entity",
            "city",
            "header",
            "title",
            "description",
        )
        name = "Мета для городов"


class ProductCitySEOExportResource(CitySEOExportResource):
    entity = fields.Field(column_name="товар", attribute="entity", widget=ForeignKeyWidget(Product, field="name"))

    class Meta(CitySEOExportResource.Meta):
        model = Product.city_set.through


class CategoryCitySEOExportResource(CitySEOExportResource, PageDescriptionFieldMixin):
    entity = fields.Field(
        column_name="категория", attribute="entity", widget=ForeignKeyWidget(SubCategory, field="name")
    )

    class Meta(CitySEOExportResource.Meta):
        model = SubCategory.city_set.through
        fields = CitySEOExportResource.Meta.fields + ("page_description",)


class TagCitySEOExportResource(CitySEOExportResource, PageDescriptionFieldMixin):
    entity = fields.Field(column_name="тэг", attribute="entity", widget=ForeignKeyWidget(Tag, field="name"))

    class Meta(CitySEOExportResource.Meta):
        model = Tag.city_set.through
        fields = CitySEOExportResource.Meta.fields + ("page_description",)


# import city seo
class NonEmptyCharWidget(CharWidget):

    def clean(self, value, row=None, **kwargs):
        val = super().clean(value, row, **kwargs)
        if len(val.strip()) == 0:
            raise ValueError("Поле не может быть пустым")
        return val


class CitySEOImportResource(resources.ModelResource):
    header = fields.Field(attribute="header", column_name="header", widget=NonEmptyCharWidget())
    title = fields.Field(attribute="title", column_name="title", widget=NonEmptyCharWidget())
    description = fields.Field(attribute="description", column_name="description", widget=NonEmptyCharWidget())

    class Meta:
        fields = (
            "id",
            "header",
            "title",
            "description",
        )
        name = "Мета для городов"


class ProductCitySEOImportResource(CitySEOImportResource):

    class Meta(CitySEOImportResource.Meta):
        model = Product.city_set.through


class CategoryCitySEOImportResource(CitySEOImportResource, PageDescriptionFieldMixin):

    class Meta(CitySEOImportResource.Meta):
        model = SubCategory.city_set.through
        fields = CitySEOImportResource.Meta.fields + ("page_description",)


class TagCitySEOImportResource(CitySEOImportResource, PageDescriptionFieldMixin):

    class Meta(CitySEOImportResource.Meta):
        model = Tag.city_set.through
        fields = CitySEOImportResource.Meta.fields + ("page_description",)
