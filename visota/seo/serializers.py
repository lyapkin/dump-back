from django.contrib.sites.shortcuts import get_current_site
from rest_framework import serializers
from parler_rest.serializers import TranslatableModelSerializer
from parler_rest.fields import TranslatedFieldsField

from .models import *


class SEOStaticPageSerializer(TranslatableModelSerializer):

    class Meta:
        model = SEOStaticPage
        fields = (
            "header",
            "title",
            "description",
            "noindex_follow",
        )

    def to_representation(self, instance):
        translated = instance.has_translation(instance.get_current_language())

        if translated:
            representation = super().to_representation(instance)
            header = representation.get("header", None)
            robots = (
                {
                    "index": False,
                    "follow": True,
                }
                if representation["noindex_follow"]
                else {}
            )
            meta = {"title": representation["title"], "description": representation["description"], "robots": robots}
            result = {"translated": translated, "header": header, "meta": meta}

        else:
            result = {"translated": False}

        return result


class SEODynamicPageSerializer(TranslatableModelSerializer):

    class Meta:
        fields = (
            "entity",
            "title",
            "description",
            "noindex_follow",
        )

    def to_representation(self, instance):
        translated = instance.has_translation(instance.get_current_language())

        if translated:
            representation = super().to_representation(instance)

            translations = representation["entity"]["translations"]
            slug = {}
            for key in translations:
                slug[key] = translations[key]["slug"]

            robots = (
                {
                    "index": False,
                    "follow": True,
                }
                if representation["noindex_follow"]
                else {}
            )
            meta = {"title": representation["title"], "description": representation["description"], "robots": robots}
            result = {"translated": translated, "meta": meta, "slug": slug}

        else:
            result = {"translated": False}

        return result


class SitemapStaticsSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=SEOStaticPage)

    class Meta:
        model = SEOStaticPage
        fields = (
            "page",
            "translations",
        )

    def to_representation(self, instance):
        represention = super().to_representation(instance)
        translations = represention["translations"]
        result = {"page": represention["page"], "langs": {}}
        for key in translations:
            result["langs"][key] = {}
            result["langs"][key]["priority"] = (
                translations.get(key, None)["priority"] if translations.get(key, None) else None
            )
            result["langs"][key]["changeFrequency"] = (
                translations.get(key, None)["change_freq"] if translations.get(key, None) else None
            )
        return result


class SitemapDynamicSerializer(TranslatableModelSerializer):

    class Meta:
        fields = (
            "entity",
            "translations",
        )

    def to_representation(self, instance):
        represention = super().to_representation(instance)
        translations = represention["entity"]["translations"]
        seo_translations = represention["translations"]
        result = {}
        for key in translations:
            result[key] = {}
            result[key]["slug"] = translations[key]["slug"]
            result[key]["lastModified"] = translations[key]["last_modified"]
            result[key]["priority"] = (
                seo_translations.get(key, None)["priority"] if seo_translations.get(key, None) else None
            )
            result[key]["changeFrequency"] = (
                seo_translations.get(key, None)["change_freq"] if seo_translations.get(key, None) else None
            )
        return result


class CategorySlugSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=SubCategory)

    class Meta:
        model = SubCategory
        fields = ("translations",)


class SEOCategoryPageSerializer(SEODynamicPageSerializer):
    entity = CategorySlugSerializer(source="category")

    class Meta(SEODynamicPageSerializer.Meta):
        model = SEOCategoryPage


class SitemapCategoriesSerializer(SitemapDynamicSerializer):
    entity = CategorySlugSerializer(source="category")
    translations = TranslatedFieldsField(shared_model=SEOCategoryPage)

    class Meta(SitemapDynamicSerializer.Meta):
        model = SEOCategoryPage


class TagSlugSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Tag)

    class Meta:
        model = Tag
        fields = ("translations",)


class SEOTagPageSerializer(SEODynamicPageSerializer):
    entity = TagSlugSerializer(source="tag")

    class Meta(SEODynamicPageSerializer.Meta):
        model = SEOTagPage


class SitemapTagSerializer(SitemapDynamicSerializer):
    entity = TagSlugSerializer(source="tag")
    translations = TranslatedFieldsField(shared_model=SEOTagPage)

    class Meta(SitemapDynamicSerializer.Meta):
        model = SEOTagPage


class ProductSlugSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Product)

    class Meta:
        model = Product
        fields = ("translations",)


class SEOProductPageSerializer(SEODynamicPageSerializer):
    entity = ProductSlugSerializer(source="product")

    class Meta(SEODynamicPageSerializer.Meta):
        model = SEOProductPage


class SitemapProductsSerializer(SitemapDynamicSerializer):
    entity = ProductSlugSerializer(source="product")
    translations = TranslatedFieldsField(shared_model=SEOProductPage)

    class Meta(SitemapDynamicSerializer.Meta):
        model = SEOProductPage


class PostSlugSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Post)

    class Meta:
        model = Post
        fields = ("translations",)


class SEOPostPageSerializer(SEODynamicPageSerializer):
    entity = PostSlugSerializer(source="post")

    class Meta(SEODynamicPageSerializer.Meta):
        model = SEOProductPage


class SitemapPostsSerializer(SitemapDynamicSerializer):
    entity = PostSlugSerializer(source="post")
    translations = TranslatedFieldsField(shared_model=SEOPostPage)

    class Meta(SitemapDynamicSerializer.Meta):
        model = SEOPostPage


class SitemapCitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = (
            "slug",
            "lang",
        )


class SitemapSerializer(serializers.ModelSerializer):
    statics = SitemapStaticsSerializer(many=True)
    categories = SitemapCategoriesSerializer(many=True)
    tags = SitemapTagSerializer(many=True)
    products = SitemapProductsSerializer(many=True)
    posts = SitemapPostsSerializer(many=True)
    cities = SitemapCitySerializer(many=True)

    class Meta:
        model = Sitemap
        fields = (
            "statics",
            "categories",
            "tags",
            "products",
            "posts",
            "cities",
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        cities = {}
        for city in representation["cities"]:
            if city["lang"] not in cities:
                cities[city["lang"]] = []
            cities[city["lang"]].append(city["slug"])
        representation["cities"] = cities

        return representation


class RedirectSerializer(TranslatableModelSerializer):
    class Meta:
        model = Redirect
        fields = ("source", "destination", "permanent")


class CitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = (
            "name",
            "slug",
        )


class CityCategorySEOSerializer(serializers.ModelSerializer):

    class Meta:
        model = CityCategorySEO
        fields = ("id", "header", "title", "description", "page_description")


class CityProductSEOSerializer(serializers.ModelSerializer):

    class Meta:
        model = CityProductSEO
        fields = (
            "id",
            "header",
            "title",
            "description",
        )


class CityTagSEOSerializer(serializers.ModelSerializer):

    class Meta:
        model = CityTagSEO
        fields = ("id", "header", "title", "description", "page_description")
