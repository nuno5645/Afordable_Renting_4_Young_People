from rest_framework import serializers
from .models import House

class HouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = House
        fields = [
            'name', 'zone', 'price', 'url', 'bedrooms', 'area', 'floor',
            'description', 'freguesia', 'concelho', 'source', 'scraped_at',
            'image_urls', 'contacted', 'discarded', 'favorite', 'house_id'
        ] 