from django.db.models import Q, F


class FilterMixin:
    def filter(self, queryset):
        query_params = self.request.query_params.copy()
        query_params.pop("page", None)

        pks = query_params.pop("pk", None)
        if pks is not None and len(pks) > 0:
            return queryset.filter(pk__in=pks)

        price_min = query_params.get("price_min")
        query_params.pop("price_min", None)
        price_max = query_params.get("price_max")
        query_params.pop("price_max", None)
        price_min_valid = True
        price_max_valid = True

        try:
            price_min = int(price_min)
        except:
            price_min_valid = False

        try:
            price_max = int(price_max)
        except:
            price_max_valid = False

        if price_max_valid and price_min_valid:
            queryset = queryset.filter(current_price__range=[price_min, price_max])
        elif price_max_valid:
            queryset = queryset.filter(current_price__lte=price_max)
        elif price_min_valid:
            queryset = queryset.filter(current_price__gte=price_min)

        searchline = query_params.get("search")
        query_params.pop("search", None)
        searchline = searchline.strip() if isinstance(searchline, str) else None
        if searchline is not None:
            searchline = searchline.split()
            queryset = queryset.filter(*[Q(translations__name__icontains=q) for q in searchline])

        presence = query_params.get("presence")
        query_params.pop("presence", None)
        if presence is not None and presence == "order":
            queryset = queryset.filter(is_present=False)
        elif presence is not None and presence == "stock":
            queryset = queryset.filter(is_present=True)

        sort = query_params.get("sort")
        desc = query_params.get("desc")
        query_params.pop("sort", None)
        query_params.pop("desc", None)
        if sort is None or sort == "default":
            sortQuery = None
        if sort == "price":
            sortQuery = (
                F("current_price").asc(nulls_last=True) if desc is None else F("current_price").desc(nulls_last=True)
            )
        elif sort == "name":
            sortQuery = "translations__name" if desc is None else "-translations__name"
        elif sort == "popularity":
            sortQuery = "views" if desc is None else "-views"

        for item in query_params.lists():
            queryset = queryset.filter(
                productcharacteristic__characteristic__translations__slug=item[0],
                productcharacteristic__characteristic_value__translations__slug__in=item[1],
            ).distinct()

        if sortQuery is None:
            return queryset.order_by("translations__priority", "id")
        else:
            return queryset.order_by(sortQuery, "translations__priority", "id")


class CleanMetaDataModelFormMixin:
    def _clean_metadata(self, cleaned_data):
        if len(cleaned_data["title"]) == 0:
            cleaned_data["title"] = self.instance.generate_seo_title(lang=self.lang, **self.data_for_seo_generation)
        if len(cleaned_data["description"]) == 0:
            cleaned_data["description"] = self.instance.generate_seo_description(
                lang=self.lang, **self.data_for_seo_generation
            )
        return cleaned_data
