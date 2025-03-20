from django.contrib.sites.shortcuts import get_current_site
from rest_framework import serializers
from parler_rest.serializers import TranslatableModelSerializer
from parler_rest.fields import TranslatedFieldsField
from django.utils.translation import get_language

from .models import *
from seo.serializers import SEOProductPageSerializer, SEOCategoryPageSerializer, SEOTagPageSerializer, CitySerializer


class ContentFieldSerializer(serializers.Field):
    def to_representation(self, value):
        domain = "http://" + str(get_current_site(self.context["request"]))
        if self.context["request"].is_secure():
            domain = "https://" + str(get_current_site(self.context["request"]))
        content = value.replace('src="/media/', f'src="{domain}/media/')
        content = content.replace("&lt;", "<")
        content = content.replace("&gt;", ">")
        content = content.replace("&quot;", "")
        return content


class CharacteriscticSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Characteristic)

    class Meta:
        model = Characteristic
        fields = ("id", "translations")

    def to_representation(self, instance):
        lang = instance.get_current_language()
        representation = super().to_representation(instance)
        if lang not in representation["translations"]:
            return None
        representation["name"] = representation["translations"][lang]["name"]
        del representation["translations"]
        return representation


class CharacteriscticValueSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=CharacteristicValue)

    class Meta:
        model = CharacteristicValue
        fields = ("id", "translations")

    def to_representation(self, instance):
        lang = instance.get_current_language()
        representation = super().to_representation(instance)
        if lang not in representation["translations"]:
            return None
        representation["name"] = representation["translations"][lang]["name"]
        del representation["translations"]
        return representation


class ProductCharacteristicSerializer(serializers.ModelSerializer):
    characteristic = CharacteriscticSerializer()
    characteristic_value = CharacteriscticValueSerializer()

    class Meta:
        model = ProductCharacteristic
        fields = ("id", "characteristic", "characteristic_value")

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if representation["characteristic"] is None or representation["characteristic_value"] is None:
            return None
        return representation


class ProductImgsSerializer(serializers.ModelSerializer):
    # img_url = serializers.CharField(source='img_url.url')
    img_url = serializers.ImageField(max_length=None, use_url=False, allow_null=True, required=False)

    class Meta:
        model = ProductImg
        fields = ("id", "img_url")


class ProductDocsSerializer(serializers.ModelSerializer):
    # translations = TranslatedFieldsField(shared_model=ProductDoc)
    url = serializers.FileField(max_length=None, use_url=False, allow_null=True, required=False)

    class Meta:
        model = ProductDoc
        fields = ("id", "url", "file_name")


class CategoryInProductSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=SubCategory)

    class Meta:
        model = SubCategory
        fields = ("id", "translations")

    def to_representation(self, instance):
        lang = instance.get_current_language()
        representation = super().to_representation(instance)
        if lang not in representation["translations"]:
            return None
        representation["name"] = representation["translations"][lang]["name"]
        representation["slug"] = representation["translations"][lang]["slug"]
        del representation["translations"]
        return representation


class ProductItemSerializer(serializers.ModelSerializer):
    characteristics = ProductCharacteristicSerializer(many=True, read_only=True, source="productcharacteristic_set")
    img_urls = ProductImgsSerializer(many=True)
    docs = serializers.SerializerMethodField()
    description = ContentFieldSerializer()
    seo = SEOProductPageSerializer()
    categories = CategoryInProductSerializer(many=True, read_only=True, source="sub_categories")

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "code",
            "slug",
            "actual_price",
            "current_price",
            "characteristics",
            "description",
            "img_urls",
            "docs",
            "is_present",
            "categories",
            "seo",
        )
        lookup_field = "slug"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["characteristics"] = [char for char in representation["characteristics"] if char is not None]
        representation["categories"] = [cat for cat in representation["categories"] if cat is not None]
        chars = {}
        for char in representation["characteristics"]:
            if char["characteristic"]["id"] not in chars:
                chars[char["characteristic"]["id"]] = char["characteristic"]
                chars[char["characteristic"]["id"]]["values"] = []
            chars[char["characteristic"]["id"]]["values"].append(char["characteristic_value"])
        representation["characteristics"] = [v for v in chars.values()]
        return representation

    def get_docs(self, obj):
        docs = obj.docs.filter(translations__language_code=get_language())
        return ProductDocsSerializer(docs, many=True, read_only=True).data


class ProductSerializer(serializers.ModelSerializer):
    characteristics = ProductCharacteristicSerializer(many=True, read_only=True, source="productcharacteristic_set")
    img_urls = ProductImgsSerializer(many=True, source="one_img")
    # description = ContentFieldSerializer()

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            # "code",
            "slug",
            "actual_price",
            "current_price",
            "characteristics",
            # "description",
            "img_urls",
            "is_present",
        )
        lookup_field = "slug"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["characteristics"] = [char for char in representation["characteristics"] if char is not None]
        chars = {}
        for char in representation["characteristics"]:
            if char["characteristic"]["id"] not in chars:
                chars[char["characteristic"]["id"]] = char["characteristic"]
                chars[char["characteristic"]["id"]]["values"] = []
            chars[char["characteristic"]["id"]]["values"].append(char["characteristic_value"])
        representation["characteristics"] = [v for v in chars.values()]
        return representation


class CharacteristicFilterSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Characteristic)

    class Meta:
        model = Characteristic
        fields = ("id", "translations")

    def to_representation(self, instance):
        lang = instance.get_current_language()
        representation = super().to_representation(instance)
        if lang not in representation["translations"]:
            return None
        representation["name"] = representation["translations"][lang]["name"]
        representation["slug"] = representation["translations"][lang]["slug"]
        del representation["translations"]
        return representation


class CharacteristicValueFilterSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=CharacteristicValue)

    class Meta:
        model = CharacteristicValue
        fields = ("id", "translations")

    def to_representation(self, instance):
        lang = instance.get_current_language()
        representation = super().to_representation(instance)
        if lang not in representation["translations"]:
            return None
        representation["name"] = representation["translations"][lang]["name"]
        representation["slug"] = representation["translations"][lang]["slug"]
        del representation["translations"]
        return representation


class ProductCharacteristicFilterSerializer(serializers.ModelSerializer):
    characteristic_value = CharacteristicValueFilterSerializer()
    characteristic = CharacteristicFilterSerializer()

    class Meta:
        model = ProductCharacteristic
        fields = ("id", "characteristic", "characteristic_value")

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if representation["characteristic"] is None or representation["characteristic_value"] is None:
            return None
        return representation


class ProductFilterSerializer(serializers.ModelSerializer):
    characteristics = ProductCharacteristicFilterSerializer(many=True, source="productcharacteristic_set")

    class Meta:
        model = Product
        fields = ("id", "characteristics")

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["characteristics"] = [char for char in representation["characteristics"] if char is not None]
        return representation


class CategoryItemSerializer(TranslatableModelSerializer):
    seo = SEOCategoryPageSerializer()
    content = ContentFieldSerializer()

    class Meta:
        model = SubCategory
        fields = ("name", "content", "seo")


class SubcategorySerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=SubCategory)
    # img = serializers.CharField(source='img.url')
    img = serializers.ImageField(max_length=None, use_url=False, allow_null=True, required=False)
    filters = ProductFilterSerializer(many=True, source="products")

    class Meta:
        model = SubCategory
        fields = (
            "id",
            "slug",
            "translations",
            "img",
            "filters",
        )

    def to_representation(self, instance):
        if instance.has_translation(instance.get_current_language()):
            representation = super().to_representation(instance)
            representation["slug"] = representation["translations"][instance.get_current_language()]["slug"]
            filters = {}
            for filter in representation["filters"]:
                if filter is None and len(filter["characteristics"]) <= 0:
                    continue

                for char in filter["characteristics"]:
                    if char["characteristic"]["id"] not in filters:
                        filters[char["characteristic"]["id"]] = {
                            "id": char["characteristic"]["id"],
                            "name": char["characteristic"]["name"],
                            "slug": char["characteristic"]["slug"],
                            "values": {},
                        }
                    if char["characteristic_value"]["id"] not in filters[char["characteristic"]["id"]]["values"]:
                        filters[char["characteristic"]["id"]]["values"][char["characteristic_value"]["id"]] = {
                            "id": char["characteristic_value"]["id"],
                            "name": char["characteristic_value"]["name"],
                            "slug": char["characteristic_value"]["slug"],
                        }

            for filter in filters.values():
                filter["values"] = filter["values"].values()
            representation["filters"] = filters.values()
            return representation


class TagItemSerializer(TranslatableModelSerializer):
    seo = SEOTagPageSerializer()

    class Meta:
        model = Tag
        fields = ("name", "seo")


class TagSerializer(TranslatableModelSerializer):
    # translations = TranslatedFieldsField(shared_model=Tag)

    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
            "slug",
        )

    # def to_representation(self, instance):
    #   representation = super().to_representation(instance)
    #   representation['slug'] = representation['translations'][instance.get_current_language()]['slug']
    #   representation['name'] = representation['translations'][instance.get_current_language()]['name']
    #   return super().to_representation(instance)


class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubcategorySerializer(many=True)
    img = serializers.ImageField(max_length=None, use_url=False, allow_null=True, required=False)

    class Meta:
        model = Category
        fields = ("name", "id", "slug", "subcategories", "img")

    def to_representation(self, instance):
        result = super().to_representation(instance)
        result["subcategories"] = [sub for sub in result["subcategories"] if sub is not None]
        return result


# city serializers
class CitySEOSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="header")
    city = CitySerializer()

    class Meta:
        fields = (
            "name",
            "content",
            "city",
            "seo",
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["seo"]["meta"]["title"] = instance.title
        representation["seo"]["meta"]["description"] = instance.description
        return representation


class CityProductSerializer(CitySEOSerializer):
    id = serializers.IntegerField(source="entity.id")
    characteristics = ProductCharacteristicSerializer(
        many=True, read_only=True, source="entity.productcharacteristic_set"
    )
    img_urls = ProductImgsSerializer(many=True, source="entity.img_urls")
    docs = serializers.SerializerMethodField(source="entity.docs")
    description = serializers.CharField(source="entity.description")
    seo = SEOProductPageSerializer(source="entity.seo")
    categories = CategoryInProductSerializer(many=True, read_only=True, source="entity.sub_categories")
    code = serializers.CharField(source="entity.code")
    slug = serializers.SlugField(source="entity.slug")
    actual_price = serializers.CharField(source="entity.actual_price")
    current_price = serializers.CharField(source="entity.current_price")
    is_present = serializers.BooleanField(source="entity.is_present")

    class Meta(CitySEOSerializer.Meta):
        model = Product.city_set.through
        fields = tuple(set(CitySEOSerializer.Meta.fields) - set(["content"])) + (
            "id",
            "name",
            "code",
            "slug",
            "actual_price",
            "current_price",
            "characteristics",
            "description",
            "img_urls",
            "docs",
            "is_present",
            "categories",
            "seo",
        )
        lookup_field = "slug"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["characteristics"] = [char for char in representation["characteristics"] if char is not None]
        representation["categories"] = [cat for cat in representation["categories"] if cat is not None]
        chars = {}
        for char in representation["characteristics"]:
            if char["characteristic"]["id"] not in chars:
                chars[char["characteristic"]["id"]] = char["characteristic"]
                chars[char["characteristic"]["id"]]["values"] = []
            chars[char["characteristic"]["id"]]["values"].append(char["characteristic_value"])
        representation["characteristics"] = [v for v in chars.values()]
        return representation

    def get_docs(self, obj):
        docs = obj.entity.docs.filter(translations__language_code=get_language())
        return ProductDocsSerializer(docs, many=True, read_only=True).data


class CityCategorySerializer(CitySEOSerializer):
    content = ContentFieldSerializer(source="page_description")
    seo = SEOCategoryPageSerializer(source="entity.seo")

    class Meta(CitySEOSerializer.Meta):
        model = SubCategory.city_set.through


class CityTagSerializer(CitySEOSerializer):
    content = ContentFieldSerializer(source="page_description")
    seo = SEOTagPageSerializer(source="entity.seo")

    class Meta(CitySEOSerializer.Meta):
        model = Tag.city_set.through
