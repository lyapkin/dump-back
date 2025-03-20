import os
import re
from decimal import Decimal
from typing import Iterable
from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator, URLValidator, RegexValidator
from parler.models import TranslatableModel, TranslatedFields
from apps.products.models import SubCategory, Product, Tag
from apps.blog.models import Post
from common.utils import generate_unique_slug
from django_ckeditor_5.fields import CKEditor5Field
from apps.products import catalog_types


# Create your models here.
class MetaGenerationRule(TranslatableModel):
    default_types = {catalog_types.TAG: "tag", catalog_types.CATEGORY: "ctg", catalog_types.PRODUCT: "prd"}
    city_types = {catalog_types.TAG: "tgc", catalog_types.CATEGORY: "ctc", catalog_types.PRODUCT: "pdc"}
    choices = {
        default_types[catalog_types.CATEGORY]: "Категория",
        default_types[catalog_types.PRODUCT]: "Товар",
        default_types[catalog_types.TAG]: "Тег",
        city_types[catalog_types.CATEGORY]: "Категория город",
        city_types[catalog_types.PRODUCT]: "Товар город",
        city_types[catalog_types.TAG]: "Тэг город",
    }

    type = models.CharField("тип", max_length=3, choices=choices, unique=True)
    instruction = models.TextField("инструкция")
    translations = TranslatedFields(
        title=models.CharField("правило генерации Title", max_length=255),
        description=models.CharField("правило генерации Description", max_length=255),
    )

    def __str__(self):
        return self.choices[self.type]

    class Meta:
        verbose_name = "правило генерации метатегов"
        verbose_name_plural = "правила генерации метатегов"

    @classmethod
    def get_default_type(cls, type):
        return cls.default_types[type]

    @classmethod
    def get_city_type(cls, type):
        return cls.city_types[type]


class Robots(models.Model):
    text = models.TextField("robots.txt")

    class Meta:
        verbose_name = "Robots"
        verbose_name_plural = "Robots"

    def __str__(self) -> str:
        return "robots.txt"


CHANGE_FREQ_CHOICES = {
    "always": "always",
    "hourly": "hourly",
    "daily": "daily",
    "weekly": "weekly",
    "monthly": "monthly",
    "yearly": "yearly",
    "never": "never",
}


class Sitemap(models.Model):
    pass


class SEOStaticPage(TranslatableModel):
    order = models.PositiveSmallIntegerField("позиция (сортировка списка в админке)")
    page = models.CharField(max_length=64, primary_key=True)
    name = models.CharField("страница", max_length=255, unique=True)
    translations = TranslatedFields(
        header=models.CharField("h1", max_length=255, unique=True),
        title=models.CharField("title", max_length=255),
        description=models.TextField("description"),
        noindex_follow=models.BooleanField('<meta name="robots" content="noindex, follow">', default=False),
        change_freq=models.CharField("changefreq", max_length=7, choices=CHANGE_FREQ_CHOICES, default="yearly"),
        priority=models.DecimalField(
            "priority",
            max_digits=2,
            decimal_places=1,
            validators=[MinValueValidator(Decimal("0.1")), MaxValueValidator(Decimal("1.0"))],
            default=1.0,
        ),
    )

    sitemap = models.ForeignKey(Sitemap, related_name="statics", on_delete=models.PROTECT, default=1)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "SEO для статических страниц"
        verbose_name_plural = "SEO для статических страниц"
        ordering = ("order",)


class SEOGenerationMixin:

    @staticmethod
    def get_default_seo_generation_rule():
        raise NotImplementedError

    def _get_seo_generation_rule(self):
        if not hasattr(self, "_seo_generation_rule"):
            rule = self.get_default_seo_generation_rule()
            self.set_seo_generation_rule(rule)

        return self._seo_generation_rule

    def set_seo_generation_rule(self, rule):
        if rule is None:
            setattr(self, "_seo_generation_rule", self.get_default_seo_generation_rule())
        setattr(self, "_seo_generation_rule", rule)

    def generate_seo_title(self, lang, name):
        rule = self._get_seo_generation_rule()
        rule.set_current_language(lang)
        return rule.title.format(name=name)

    def generate_seo_description(self, lang, name):
        rule = self._get_seo_generation_rule()
        rule.set_current_language(lang)
        return rule.description.format(name=name)

    def generate_seo_title_by_entity(self, entity):
        return self.generate_seo_title(entity.get_current_language(), entity.name)

    def generate_seo_description_by_entity(self, entity):
        return self.generate_seo_description(entity.get_current_language(), entity.name)


class SEOCategoryPage(TranslatableModel, SEOGenerationMixin):
    category = models.OneToOneField(
        SubCategory, verbose_name="категория", related_name="seo", on_delete=models.CASCADE, primary_key=True
    )
    translations = TranslatedFields(
        title=models.CharField("title", max_length=255),
        description=models.TextField("description"),
        noindex_follow=models.BooleanField('<meta name="robots" content="noindex, follow">', default=False),
        change_freq=models.CharField("changefreq", max_length=7, choices=CHANGE_FREQ_CHOICES, default="yearly"),
        priority=models.DecimalField(
            "priority",
            max_digits=2,
            decimal_places=1,
            validators=[MinValueValidator(Decimal("0.1")), MaxValueValidator(Decimal("1.0"))],
            default=1.0,
        ),
    )

    sitemap = models.ForeignKey(Sitemap, related_name="categories", on_delete=models.PROTECT, default=1)

    def __str__(self):
        return self.category.name

    class Meta:
        verbose_name = "SEO для категорий"
        verbose_name_plural = "SEO для категорий"

    @staticmethod
    def get_default_seo_generation_rule():
        return MetaGenerationRule.objects.get(type=MetaGenerationRule.get_default_type(catalog_types.CATEGORY))


class SEOTagPage(TranslatableModel, SEOGenerationMixin):
    tag = models.OneToOneField(Tag, verbose_name="тег", related_name="seo", on_delete=models.CASCADE, primary_key=True)
    translations = TranslatedFields(
        title=models.CharField("title", max_length=255),
        description=models.TextField("description"),
        noindex_follow=models.BooleanField('<meta name="robots" content="noindex, follow">', default=False),
        change_freq=models.CharField("changefreq", max_length=7, choices=CHANGE_FREQ_CHOICES, default="yearly"),
        priority=models.DecimalField(
            "priority",
            max_digits=2,
            decimal_places=1,
            validators=[MinValueValidator(Decimal("0.1")), MaxValueValidator(Decimal("1.0"))],
            default=1.0,
        ),
    )

    sitemap = models.ForeignKey(Sitemap, related_name="tags", on_delete=models.PROTECT, default=1)

    def __str__(self):
        return self.tag.name

    class Meta:
        verbose_name = "SEO для тегов"
        verbose_name_plural = "SEO для тегов"

    @staticmethod
    def get_default_seo_generation_rule():
        return MetaGenerationRule.objects.get(type=MetaGenerationRule.get_default_type(catalog_types.TAG))


class SEOProductPage(TranslatableModel, SEOGenerationMixin):
    product = models.OneToOneField(
        Product, verbose_name="Товар", related_name="seo", on_delete=models.CASCADE, primary_key=True
    )
    translations = TranslatedFields(
        title=models.CharField("title", max_length=255),
        description=models.TextField("description"),
        noindex_follow=models.BooleanField('<meta name="robots" content="noindex, follow">', default=False),
        change_freq=models.CharField("changefreq", max_length=7, choices=CHANGE_FREQ_CHOICES, default="yearly"),
        priority=models.DecimalField(
            "priority",
            max_digits=2,
            decimal_places=1,
            validators=[MinValueValidator(Decimal("0.1")), MaxValueValidator(Decimal("1.0"))],
            default=1.0,
        ),
    )

    sitemap = models.ForeignKey(Sitemap, related_name="products", on_delete=models.PROTECT, default=1)

    def __str__(self):
        return self.product.name

    class Meta:
        verbose_name = "SEO для товара"
        verbose_name_plural = "SEO для товара"

    @staticmethod
    def get_default_seo_generation_rule():
        return MetaGenerationRule.objects.get(type=MetaGenerationRule.get_default_type(catalog_types.PRODUCT))

    def generate_seo_title(self, lang, name, price):
        rule = self._get_seo_generation_rule()
        rule.set_current_language(lang)
        return rule.title.format(name=name, price=price)

    def generate_seo_description(self, lang, name, price):
        rule = self._get_seo_generation_rule()
        rule.set_current_language(lang)
        return rule.description.format(name=name, price=price)

    def generate_seo_title_by_entity(self, entity):
        price = entity.current_price or entity.actual_price or ""
        return self.generate_seo_title(entity.get_current_language(), entity.name, price)

    def generate_seo_description_by_entity(self, entity):
        price = entity.current_price or entity.actual_price or ""
        return self.generate_seo_description(entity.get_current_language(), entity.name, price)


class SEOPostPage(TranslatableModel):
    post = models.OneToOneField(
        Post, verbose_name="пост", related_name="seo", on_delete=models.CASCADE, primary_key=True
    )
    translations = TranslatedFields(
        title=models.CharField("title", max_length=255),
        description=models.TextField("description"),
        noindex_follow=models.BooleanField('<meta name="robots" content="noindex, follow">', default=False),
        change_freq=models.CharField("changefreq", max_length=7, choices=CHANGE_FREQ_CHOICES, default="yearly"),
        priority=models.DecimalField(
            "priority",
            max_digits=2,
            decimal_places=1,
            validators=[MinValueValidator(Decimal("0.1")), MaxValueValidator(Decimal("1.0"))],
            default=1.0,
        ),
    )

    sitemap = models.ForeignKey(Sitemap, related_name="posts", on_delete=models.PROTECT, default=1)

    def __str__(self):
        return self.post.title

    class Meta:
        verbose_name = "SEO для поста"
        verbose_name_plural = "SEO для поста"


class AbstractFile(models.Model):
    name = models.CharField("название", max_length=30, unique=True)
    content = models.TextField("код", null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class JSFile(AbstractFile):

    class Meta:
        verbose_name = "js"
        verbose_name_plural = "js"

    def save(self, *args, **kwargs):
        os.makedirs(os.path.join(settings.STATIC_ROOT, "seo", "js"), exist_ok=True)
        with open(os.path.join(settings.STATIC_ROOT, "seo", "js", self.name), "w") as f:
            file = File(f)
            file.write(self.content)
        super().save(*args, **kwargs)


class CSSFile(AbstractFile):

    class Meta:
        verbose_name = "css"
        verbose_name_plural = "css"

    def save(self, *args, **kwargs):
        os.makedirs(os.path.join(settings.STATIC_ROOT, "seo", "css"), exist_ok=True)
        with open(os.path.join(settings.STATIC_ROOT, "seo", "css", self.name), "w") as f:
            file = File(f)
            file.write(self.content)
        super().save(*args, **kwargs)


class StandardURLField(models.URLField):
    default_validators = [URLValidator(["https", "http"])]

    def clean(self, value, model_instance):
        result = super().clean(value, model_instance)
        return StandardURLField._edit_url(result, model_instance.language_code)

    @staticmethod
    def _edit_url(value, locale):
        result = StandardURLField._to_no_www_domain(value)
        result = StandardURLField._trim_query_params(result)
        result = StandardURLField._trim_html(result)
        result = StandardURLField._insert_locale(result, locale)
        result = StandardURLField._trailing_slash(result)
        return result

    @staticmethod
    def _to_no_www_domain(value):
        return re.sub(r"^(http[s]?://)?(www\.)?", "https://", value, flags=re.IGNORECASE)

    @staticmethod
    def _trim_html(value):
        return re.sub(r".html$", "/", value, flags=re.IGNORECASE)

    @staticmethod
    def _trim_query_params(value):
        return re.sub(r"\?(.)*", "", value)

    @staticmethod
    def _insert_locale(value, locale):
        available_langs_re = "|".join([t[0] for t in settings.LANGUAGES])

        split_base = re.split(rf"^(https://{re.escape(settings.SITE_DOMAIN)})", value, maxsplit=1)
        # Результат ["", "https://visota13.ru", "/{path}"]
        base = split_base[1]
        print(split_base)

        split_locale = re.split(rf"^/({available_langs_re})/", split_base[2])
        # Результат ["", "{locale}", "{path}"] если язык указан
        # иначе ["/{path}"]
        path = split_locale[-1]
        print(split_locale)

        # Нет языка в url
        if len(split_locale) == 1:
            return base + f"/{locale}" + path

        # Язык в url совпадает с языком настраемого редиректа в админке
        if split_locale[1] == locale:
            return value

        # Язык в url не совпадает с языком настраемого редиректа в админке
        return base + f"/{locale}/" + path

    @staticmethod
    def _trailing_slash(value):
        if re.search(r"/$", value) is not None:
            return value
        return value + "/"


class GhostRedirect(TranslatableModel):
    translations = TranslatedFields()

    class Meta:
        verbose_name = "редиректы"
        verbose_name_plural = "редиректы"

    def __str__(self):
        return "Список редиректов"


class Redirect(TranslatableModel):
    parent = models.ForeignKey(GhostRedirect, on_delete=models.PROTECT)

    translations = TranslatedFields(
        src=StandardURLField(
            "откуда",
            unique=True,
            validators=[
                RegexValidator(
                    regex=rf"^(http[s]?://)?(www\.)?{re.escape(settings.SITE_DOMAIN)}",
                    message=f"Url дожен быть с доменом {settings.SITE_DOMAIN}",
                    code="invalid_url",
                )
            ],
        ),
        to=StandardURLField(
            "куда",
            validators=[
                RegexValidator(
                    regex=rf"^(http[s]?://)?(www\.)?{re.escape(settings.SITE_DOMAIN)}",
                    message=f"Url дожен быть с доменом {settings.SITE_DOMAIN}",
                    code="invalid_url",
                )
            ],
        ),
        source=models.CharField(blank=True, max_length=200),
        destination=models.CharField(blank=True, max_length=200),
        permanent=models.BooleanField("тип редиректа постоянный", default=True),
    )

    class Meta:
        verbose_name = "редирект"
        verbose_name_plural = "редиректы"

    def __str__(self):
        return f"Откуда: {self.src}; Куда: {self.to};"

    def clean(self):
        self.source = Redirect._to_relative_url(self.src)
        self.destination = Redirect._to_relative_url(self.to)

    @staticmethod
    def _to_relative_url(value):
        available_langs_re = "|".join([t[0] for t in settings.LANGUAGES])
        result = re.sub(
            rf"^(http[s]?://)?(www\.)?{re.escape(settings.SITE_DOMAIN)}/({available_langs_re})/",
            "",
            value,
            flags=re.IGNORECASE,
        )
        return "/" + result


# City SEO
class City(models.Model):
    name = models.CharField("город", max_length=128, unique=True)
    slug = models.SlugField("url", max_length=128, unique=True, blank=True)

    products = models.ManyToManyField(Product, through="CityProductSEO")
    categories = models.ManyToManyField(SubCategory, through="CityCategorySEO")
    tags = models.ManyToManyField(Tag, through="CityTagSEO")

    lang = models.CharField(
        "языковая для города",
        max_length=2,
        choices=settings.LANGUAGES,
        default="ru",
    )

    sitemap = models.ForeignKey(Sitemap, related_name="cities", on_delete=models.PROTECT, default=1)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "город"
        verbose_name_plural = "города"

    def save(self, *args, **kwargs):
        if not self.slug.strip():
            self.slug = generate_unique_slug(City, self.name)
        return super().save(*args, **kwargs)


class CitySEO(models.Model, SEOGenerationMixin):
    city = models.ForeignKey(City, verbose_name="город", on_delete=models.CASCADE)

    header = models.CharField("h1", max_length=255)
    title = models.CharField("title", max_length=255)
    description = models.TextField("description")

    class Meta:
        abstract = True
        verbose_name = "SEO по городу"
        verbose_name_plural = "SEO по городам"

    def __str__(self):
        return f"{self.city.name} - {self.entity.name}"

    @classmethod
    def bind_entity_to_cities(cls, entity, cities):
        rule = cls.get_default_seo_generation_rule()
        rule.set_current_language(entity.get_current_language())
        seo_list = []
        for city in cities:
            header = entity.name
            title = cls.generate_seo_data(entity=entity, city_name=city.name, rule=rule.title)
            description = cls.generate_seo_data(entity=entity, city_name=city.name, rule=rule.description)
            seo = cls(entity=entity, city=city, header=header, title=title, description=description)
            seo_list.append(seo)
        return cls.objects.bulk_create(seo_list)

    @staticmethod
    def generate_seo_data(entity, city_name, rule):
        return rule.format(name=entity.name, city=city_name)

    def generate_seo_title(self, lang, name, city_name):
        rule = self._get_seo_generation_rule()
        rule.set_current_language(lang)
        return rule.title.format(name=name, city=city_name)

    def generate_seo_description(self, lang, name, city_name):
        rule = self._get_seo_generation_rule()
        rule.set_current_language(lang)
        return rule.description.format(name=name, city=city_name)

    def generate_seo_title_by_entity(self, entity, city_name):
        return self.generate_seo_title(entity.get_current_language(), entity.name, city_name)

    def generate_seo_description_by_entity(self, entity, city_name):
        return self.generate_seo_description(entity.get_current_language(), entity.name, city_name)


class CityProductSEO(CitySEO):
    entity = models.ForeignKey(Product, related_name="city_seo_set", on_delete=models.CASCADE)

    class Meta(CitySEO.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=("city", "entity"),
                name="unique_city_product",
            ),
        ]

    @staticmethod
    def generate_seo_data(entity, city_name, rule):
        price = entity.current_price or entity.actual_price or ""
        return rule.format(name=entity.name, city=city_name, price=price)

    def generate_seo_title(self, lang, name, city_name, price):
        rule = self._get_seo_generation_rule()
        rule.set_current_language(lang)
        return rule.title.format(name=name, city=city_name, price=price)

    def generate_seo_description(self, lang, name, city_name, price):
        rule = self._get_seo_generation_rule()
        rule.set_current_language(lang)
        return rule.description.format(name=name, city=city_name, price=price)

    def generate_seo_title_by_entity(self, entity, city_name):
        price = entity.current_price or entity.actual_price or ""
        return self.generate_seo_title(entity.get_current_language(), entity.name, city_name, price)

    def generate_seo_description_by_entity(self, entity, city_name):
        price = entity.current_price or entity.actual_price or ""
        return self.generate_seo_description(entity.get_current_language(), entity.name, city_name, price)

    @staticmethod
    def get_default_seo_generation_rule():
        return MetaGenerationRule.objects.get(type=MetaGenerationRule.get_city_type(catalog_types.PRODUCT))


class CityCategorySEO(CitySEO):
    entity = models.ForeignKey(SubCategory, related_name="city_seo_set", on_delete=models.CASCADE)
    page_description = CKEditor5Field("описание категории", config_name="extends2", null=True, blank=True)

    class Meta(CitySEO.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=("city", "entity"),
                name="unique_city_category",
            ),
        ]

    @staticmethod
    def get_default_seo_generation_rule():
        return MetaGenerationRule.objects.get(type=MetaGenerationRule.get_city_type(catalog_types.CATEGORY))


class CityTagSEO(CitySEO):
    entity = models.ForeignKey(Tag, related_name="city_seo_set", on_delete=models.CASCADE)
    page_description = CKEditor5Field("описание тега", config_name="extends2", null=True, blank=True)

    class Meta(CitySEO.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=("city", "entity"),
                name="unique_city_tag",
            ),
        ]

    @staticmethod
    def get_default_seo_generation_rule():
        return MetaGenerationRule.objects.get(type=MetaGenerationRule.get_city_type(catalog_types.TAG))
