from django import forms
from import_export.forms import ImportExportFormBase, ImportForm, ExportForm
from parler.forms import TranslatableModelForm
from .mixins import CleanMetaDataModelFormMixin


class SEOInlineFormModel(TranslatableModelForm, CleanMetaDataModelFormMixin):
    title = forms.CharField(label="title", max_length=255, required=False)
    description = forms.CharField(label="description", widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        data_for_seo_generation = kwargs.pop("data_for_seo_generation", None)
        lang = kwargs.pop("lang", None)
        super().__init__(*args, **kwargs)
        self.data_for_seo_generation = data_for_seo_generation
        self.lang = lang

    def has_changed(self):
        title = self.initial.get("title", None)
        description = self.initial.get("description", None)
        if not title or not description or len(title) == 0 or len(description) == 0:
            return True
        return super().has_changed()

    def clean(self):
        cleaned_data = super().clean()

        return self._clean_metadata(cleaned_data)


class CitySEOInlineFormModel(forms.ModelForm, CleanMetaDataModelFormMixin):
    title = forms.CharField(label="title", max_length=255, required=False)
    description = forms.CharField(label="description", widget=forms.Textarea, required=False)
    header = forms.CharField(label="h1", max_length=255, required=False)

    def __init__(self, *args, **kwargs):
        data_for_seo_generation = kwargs.pop("data_for_seo_generation", None)
        city_name = kwargs.pop("city_name", None)
        lang = kwargs.pop("lang", None)
        super().__init__(*args, **kwargs)
        self.data_for_seo_generation = data_for_seo_generation
        self.lang = lang
        self.city_name = city_name

    def has_changed(self):
        if self.initial and (
            len(self.initial["header"].strip()) == 0
            or len(self.initial["title"].strip()) == 0
            or len(self.initial["description"].strip()) == 0
        ):
            return True
        return super().has_changed()

    def clean(self):
        cleaned_data = super().clean()

        if len(cleaned_data["header"]) == 0:
            cleaned_data["header"] = self.data_for_seo_generation["name"]

        return self._clean_metadata(cleaned_data)


class CitySEOImportExportFormBase(ImportExportFormBase):

    def _init_resources(self, resources):
        if not resources:
            raise ValueError("no defined resources")
        self.fields["resource"].choices = [(i, resource.get_display_name()) for i, resource in enumerate(resources)]
        if len(resources) == 1:
            self.fields["resource"].disabled = True
            self.initial["resource"] = "0"


class CitySEOImportForm(ImportForm, CitySEOImportExportFormBase):
    import_file = forms.FileField(label="CSV Файл", widget=forms.FileInput(attrs={"accept": ".csv"}))


class CitySEOExportForm(ExportForm, CitySEOImportExportFormBase):
    pass
