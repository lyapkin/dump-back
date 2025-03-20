from django.urls import path, include
from rest_framework import routers


from .views import VacancyApi

router = routers.SimpleRouter()
router.register('', VacancyApi)

urlpatterns = [
    path('', include(router.urls)),
]