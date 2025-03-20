from datetime import date
from rest_framework import viewsets, mixins
from django.db.models import Q

from .models import *
from .serializers import *


class PromoApi(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = Promo.objects.filter(Q(is_active=True), Q(last_day__gte=date.today())).order_by("-last_day")
    serializer_class = PromoSerializer
