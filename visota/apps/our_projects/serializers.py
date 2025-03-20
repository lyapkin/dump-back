from django.contrib.sites.shortcuts import get_current_site
from rest_framework import serializers
from django.conf import settings

from .models import *


class ContentFieldSerializer(serializers.Field):
    def to_representation(self, value):
        domain = 'http://'+str(get_current_site(self.context['request']))
        if self.context['request'].is_secure():
            domain = 'https://'+str(get_current_site(self.context['request']))
        content = value.replace("src=\"/media/", f"src=\"{domain}/media/")
        content = content.replace("&lt;", "<")
        content = content.replace("&gt;", ">")
        content = content.replace("&quot;", "")
        return content
    

class ProjectSerializer(serializers.ModelSerializer):
    content = ContentFieldSerializer()

    class Meta:
        model = Project
        fields = ("id", "title", "content", 'location')


class ProjectPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        exclude = ("content",)