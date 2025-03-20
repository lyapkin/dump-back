from django.urls import path, include
from rest_framework import routers


from .views import *

router = routers.SimpleRouter(trailing_slash=True)
router.register("products", ProductApi)
router.register("categories", CategoryApi)
router.register("tags", TagApi)

city_router = routers.SimpleRouter(trailing_slash=True)
city_router.register("products", CityProductApi)
city_router.register("categories", CityCategoryApi)
city_router.register("tags", CityTagApi)

urlpatterns = [
    path("", include(router.urls)),
    path("city/<slug:city_slug>/", include(city_router.urls)),
    # path('preview/', ProductGroupedByCategoryApi.as_view(), name="products_preview")
]
