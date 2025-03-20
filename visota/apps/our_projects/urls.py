from django.urls import path, include
from rest_framework import routers


from .views import ProjectApi

router = routers.SimpleRouter()
router.register('', ProjectApi)

urlpatterns = [
    path('', include(router.urls)),
]