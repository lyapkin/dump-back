import logging
from rest_framework import viewsets, mixins

from .models import *
from .serializers import *


logger = logging.getLogger("visota.forms")


class CommonRequestApi(viewsets.GenericViewSet, mixins.CreateModelMixin):
    def create(self, request, *args, **kwargs):
        logger.info(f"{request.path} starts form handling")
        logger.info(f"Initial data: {request.data}")
        response = super().create(request, *args, **kwargs)
        logger.info(f"{request.path} ends form handling")
        return response


class ConsultationRequestApi(CommonRequestApi):
    queryset = ConsultationRequest.objects.all()
    serializer_class = ConsultationRequestSerializer


class OfferRequestApi(CommonRequestApi):
    queryset = CommercialOfferRequest.objects.all()
    serializer_class = OfferRequestSerializer


class PriceRequestApi(CommonRequestApi):
    queryset = PriceRequest.objects.all()
    serializer_class = PriceRequestSerializer


class OrderApi(CommonRequestApi):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class SampleRequestApi(CommonRequestApi):
    queryset = SampleRequest.objects.all()
    serializer_class = SampleRequestSerializer
