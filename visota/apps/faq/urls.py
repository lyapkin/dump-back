from django.urls import path, include
from rest_framework import routers


from .views import FAQApi

router = routers.SimpleRouter()
router.register('', FAQApi)

urlpatterns = [
    path('', include(router.urls)),
]