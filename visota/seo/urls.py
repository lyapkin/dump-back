from django.urls import path, include
from rest_framework import routers


from .views import *

router = routers.SimpleRouter(trailing_slash=True)
router.register("static", MetaStaticApi)
router.register("category", MetaCategoryApi)
router.register("tag", MetaTagApi)
router.register("product", MetaProductApi)
router.register("blog", MetaPostApi)
router.register("sitemap", SitemapApi)
router.register("city-seo/categories", CityCategorySEOApi)
router.register("city-seo/products", CityProductSEOApi)
router.register("city-seo/tags", CityTagSEOApi)

urlpatterns = [path("meta/", include(router.urls)), path("redirects/", RedirectApi.as_view())]
