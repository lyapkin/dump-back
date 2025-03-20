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
    

class FAQSerializer(serializers.ModelSerializer):
    answer = ContentFieldSerializer()

    class Meta:
        model = FAQ
        fields = '__all__'


class FAQCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQCategory
        fields = '__all__'


class FAQCategoriesListSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return {
            "faqs": FAQSerializer(instance["faqs"], many=True, context=self.context).data,
            "categories": FAQCategorySerializer(instance["categories"], many=True).data
        }