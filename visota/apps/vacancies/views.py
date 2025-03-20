from rest_framework import viewsets
from rest_framework.response import Response

from .models import *
from .serializers import *

class VacancyApi(viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"
    queryset = Vacancy.objects.filter(is_open=True).order_by("-last_modified")
    serializer_action_classes = {
        "list": VacancySerializer,
        "retrieve": VacancyItemSerializer
    }

    # def get_queryset(self):
    #     return super().get_queryset().filter(is_open=True)

    def get_serializer_class(self):
        return self.serializer_action_classes[self.action]
    
    