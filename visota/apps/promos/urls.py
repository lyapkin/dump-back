from django.urls import path, include
from rest_framework import routers


from .views import PromoApi

router = routers.SimpleRouter(trailing_slash=False)
router.register('', PromoApi)

urlpatterns = [
    path('', include(router.urls)),
]