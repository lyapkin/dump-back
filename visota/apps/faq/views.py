from rest_framework import viewsets, mixins
from rest_framework.response import Response

from .models import *
from .serializers import *


class FAQApi(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = FAQ.objects.order_by("-id")
    serializer_class = FAQSerializer
    
    def list(self, request, *args, **kwargs):
        response_obj = {
            "faqs": self.get_queryset(),
            "categories": FAQCategory.objects.all()
        }
        return Response(FAQCategoriesListSerializer(response_obj, context={'request': request}).data)