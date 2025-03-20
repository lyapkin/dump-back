from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import get_language
from rest_framework import viewsets
from rest_framework.response import Response

from .models import *
from .serializers import *


class ArticleApi(viewsets.ReadOnlyModelViewSet):
    lookup_field = "translations__slug"
    lookup_url_kwarg = 'slug'
    queryset = Post.objects.translated().order_by("-id")
    serializer_action_classes = {
        "list": ArticlePreviewSerializer,
        "retrieve": ArticleSerializer
    }

    def retrieve(self, request, slug=None, *args, **kwargs):
        # return super().retrieve(request, *args, **kwargs)
        try:
          instance = self.get_object()
        except Http404:
          active_slug = get_object_or_404(PostRedirectFrom, lang=get_language(), old_slug=slug)
          return redirect(f'/{active_slug.to.slug}/', permanent=True)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_queryset(self):
        return Post.objects.translated().order_by("-id")

    def get_serializer_class(self):
        return self.serializer_action_classes[self.action]
