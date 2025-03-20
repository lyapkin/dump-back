from django.contrib.sites.shortcuts import get_current_site
from rest_framework import serializers
from django.conf import settings

from .models import *
    

class BonusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bonus
        fields = '__all__'


class PromoSerializer(serializers.ModelSerializer):
    bonus = BonusSerializer()

    class Meta:
        model = Promo
        exclude = ['is_active']


