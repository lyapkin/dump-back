from rest_framework import viewsets

from .models import *
from .serializers import *


class ProjectApi(viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"
    queryset = Project.objects.order_by("-id")
    serializer_action_classes = {
        "list": ProjectPreviewSerializer,
        "retrieve": ProjectSerializer
    }

    def get_serializer_class(self):
        return self.serializer_action_classes[self.action]

