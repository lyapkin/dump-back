import math
from django.http import Http404, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from rest_framework import viewsets, generics, mixins
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q, F
from django.utils.translation import get_language
from django.db.models import Prefetch

from .models import *
from .serializers import *
from .mixins import FilterMixin


class ProductAPIListPagination(PageNumberPagination):
    page_size = 12

    def get_paginated_response(self, data):
        response = super().get_paginated_response(data)
        response.data["page_count"] = math.ceil(response.data["count"] / self.get_page_size(self.request))
        return response


class ProductApi(viewsets.ReadOnlyModelViewSet, FilterMixin):
    queryset = Product.objects.filter(translations__language_code=get_language())
    serializer_action_classes = {"list": ProductSerializer, "retrieve": ProductItemSerializer}
    pagination_class = ProductAPIListPagination
    lookup_field = "translations__slug"
    lookup_url_kwarg = "slug"

    def retrieve(self, request, slug=None, *args, **kwargs):
        # return super().retrieve(request, *args, **kwargs)
        try:
            instance = get_object_or_404(Product, translations__language_code=get_language(), translations__slug=slug)
        except Http404:
            active_slug = get_object_or_404(ProductRedirectFrom, lang=get_language(), old_slug=slug)
            return redirect(f"/{active_slug.to.slug}/", permanent=True)
        instance.views = F("views") + 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_serializer_class(self):
        return self.serializer_action_classes[self.action]

    def get_queryset(self):
        queryset = Product.objects.filter(translations__language_code=get_language()).order_by(
            "translations__priority", "id"
        )

        return self.filter(queryset=queryset)

    @action(detail=False)
    def cart(self, request):
        query_params = request.query_params

        pks = query_params.getlist("pk")
        if pks is not None and len(pks) > 0:
            pks = map(lambda item: int(item), pks)
            queryset = Product.objects.filter(id__in=pks)
            cartSerializer = ProductSerializer(queryset.order_by(*pks), many=True, context={"request": request})

            return Response(cartSerializer.data)

        return Response(status=404)


class CategoryApi(viewsets.ReadOnlyModelViewSet, FilterMixin):
    queryset = (
        Category.objects.translated()
        .order_by("priority")
        .prefetch_related(Prefetch("subcategories", queryset=SubCategory.objects.all().order_by("priority")))
    )
    serializer_class = CategorySerializer
    # pagination_class = ProductAPIListPagination
    lookup_field = "translations__slug"
    lookup_url_kwarg = "slug"

    def retrieve(self, request, slug=None, *args, **kwargs):
        try:
            cat = SubCategory.objects.get(translations__slug=slug, translations__language_code=get_language())
            serializer = CategoryItemSerializer(cat, context={"request": request})
            return Response(serializer.data)
        except SubCategory.DoesNotExist:
            active_slug = get_object_or_404(CategoryRedirectFrom, lang=get_language(), old_slug=slug)
            return redirect(f"/{active_slug.to.slug}/", permanent=True)

    @action(detail=True, serializer_class=ProductSerializer, pagination_class=ProductAPIListPagination)
    def products(self, request, slug=None):
        category = get_object_or_404(SubCategory, translations__slug=slug)

        products = category.products.filter(translations__language_code=get_language())

        products = self.filter(products)

        page = self.paginate_queryset(products)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(products, many=True)

        return Response(serializer.data)


class TagApi(viewsets.ReadOnlyModelViewSet, FilterMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = "translations__slug"
    lookup_url_kwarg = "slug"

    def get_queryset(self):
        return super().get_queryset().filter(translations__language_code=get_language())

    def retrieve(self, request, slug=None, *args, **kwargs):
        try:
            tag = Tag.objects.get(translations__slug=slug, translations__language_code=get_language())
            serializer = TagItemSerializer(tag)
            return Response(serializer.data)
        except Tag.DoesNotExist:
            active_slug = get_object_or_404(TagRedirectFrom, lang=get_language(), old_slug=slug)
            return redirect(f"/{active_slug.to.slug}/", permanent=True)

    @action(detail=True, serializer_class=ProductSerializer, pagination_class=ProductAPIListPagination)
    def products(self, request, slug=None):
        tag = get_object_or_404(Tag, translations__slug=slug)

        products = tag.products.translated().all()

        products = self.filter(products)

        page = self.paginate_queryset(products)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(products, many=True)

        return Response(serializer.data)


# city APIs
class CitySEOApi(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    lookup_field = "translations__slug"
    lookup_url_kwarg = "slug"

    def retrieve(self, request, city_slug=None, slug=None, *args, **kwargs):
        try:
            instance = self.get_object(slug, city_slug)
        except Http404:
            active_slug = get_object_or_404(self.redirect_class, lang=get_language(), old_slug=slug)
            return redirect(f"/{active_slug.to.slug}/", permanent=True)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_object(self, slug, city_slug):
        lang = get_language()
        qs = self.get_queryset().filter(
            entity__translations__slug=slug,
            entity__translations__language_code=lang,
            city__slug=city_slug,
            city__lang=lang,
        )
        qs = self.preload_related(qs)
        obj = get_object_or_404(
            qs,
            entity__translations__slug=slug,
            entity__translations__language_code=lang,
            city__slug=city_slug,
            city__lang=lang,
        )
        return obj

    def preload_related(self, qs):
        return qs.select_related("entity__seo", "city")


class CityProductApi(CitySEOApi):
    queryset = Product.city_set.through.objects.all()
    serializer_class = CityProductSerializer
    redirect_class = ProductRedirectFrom

    def preload_related(self, qs):
        return (
            super()
            .preload_related(qs)
            .prefetch_related(
                "entity__productcharacteristic_set__characteristic",
                "entity__productcharacteristic_set__characteristic_value",
            )
        )


class CityCategoryApi(CitySEOApi):
    queryset = SubCategory.city_set.through.objects.all()
    redirect_class = CategoryRedirectFrom
    serializer_class = CityCategorySerializer


class CityTagApi(CitySEOApi):
    queryset = Tag.city_set.through.objects.all()
    serializer_class = CityTagSerializer
    redirect_class = TagRedirectFrom
