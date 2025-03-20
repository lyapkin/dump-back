from django.urls import path, include
from rest_framework import routers


from .views import *

router = routers.SimpleRouter()
router.register('consultation', ConsultationRequestApi)
router.register('price', PriceRequestApi)
router.register('order', OrderApi)
router.register('samples', SampleRequestApi)
router.register('offer', OfferRequestApi)

urlpatterns = [
    path('', include(router.urls)),
]