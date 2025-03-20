from django.urls import path, include
from rest_framework import routers


from .views import ArticleApi

router = routers.SimpleRouter()
router.register('', ArticleApi)

urlpatterns = [
    path('', include(router.urls)),
]