from rest_framework import serializers
from .models import House, Photo, Parish, County, District, MainRun, ScraperRun
import re

class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ['id', 'name']

class CountySerializer(serializers.ModelSerializer):
    district = DistrictSerializer(read_only=True)
    
    class Meta:
        model = County
        fields = ['id', 'name', 'district']

class ParishSerializer(serializers.ModelSerializer):
    county = CountySerializer(read_only=True)
    
    class Meta:
        model = Parish
        fields = ['id', 'name', 'county']

class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['image_url', 'order']

class HouseSerializer(serializers.ModelSerializer):
    bedrooms = serializers.SerializerMethodField()
    area = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    is_contacted = serializers.SerializerMethodField()
    is_discarded = serializers.SerializerMethodField()
    photos = PhotoSerializer(many=True, read_only=True)
    parish = ParishSerializer(read_only=True)
    county = CountySerializer(read_only=True)
    district = DistrictSerializer(read_only=True)
    
    class Meta:
        model = House
        fields = [
            'name', 'zone', 'price', 'url', 'bedrooms', 'area', 'floor',
            'description', 'parish', 'county', 'district', 'source', 'scraped_at',
            'house_id', 'is_favorite', 'is_contacted', 'is_discarded', 'photos'
        ]
    
    def get_bedrooms(self, obj):
        """
        Clean the bedrooms field to extract just the number.
        Converts formats like 'T2', 't2', etc. to just '2'.
        """
        if not obj.bedrooms:
            return "0"
            
        # Use regex to extract digits from the bedrooms field
        # This will handle cases like "T2", "t2", "2 bedrooms", etc.
        match = re.search(r'(\d+)', obj.bedrooms)
        if match:
            return match.group(1)
        return "0"  # Default to 0 if no number is found
        
    def get_area(self, obj):
        """
        Clean the area field to extract just the number.
        Handles cases where area might contain text or formatting.
        """
        if isinstance(obj.area, str):
            # Remove any non-numeric characters except decimal point
            area = ''.join(c for c in obj.area if c.isdigit() or c == '.')
            try:
                # Try to convert to float and then to string
                return str(float(area))
            except ValueError:
                return "0"
                
        # Default case, convert to string
        return str(obj.area)

    def get_is_favorite(self, obj):
        """Check if the house is favorited by the current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorited_by.filter(id=request.user.id).exists()
        return False

    def get_is_contacted(self, obj):
        """Check if the house is marked as contacted by the current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.contacted_by.filter(id=request.user.id).exists()
        return False

    def get_is_discarded(self, obj):
        """Check if the house is discarded by the current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.discarded_by.filter(id=request.user.id).exists()
        return False


class ScraperRunSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    
    class Meta:
        model = ScraperRun
        fields = [
            'id', 'scraper', 'name', 'status', 'start_time', 'end_time',
            'execution_time', 'total_houses', 'new_houses', 'error_message'
        ]
    
    def get_name(self, obj):
        """Format the scraper name to be more readable"""
        return obj.scraper.replace('_', ' ').title()


class MainRunSerializer(serializers.ModelSerializer):
    scraper_runs = ScraperRunSerializer(many=True, read_only=True)
    
    class Meta:
        model = MainRun
        fields = [
            'id', 'status', 'start_time', 'end_time', 'execution_time',
            'total_houses', 'new_houses', 'error_message', 'scraper_runs'
        ] 