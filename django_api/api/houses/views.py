from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import House
from .serializers import HouseSerializer
from .settings import ROOM_RENTAL_TITLE_TERMS
import json
from pathlib import Path
from datetime import datetime

# Create your views here.

class HouseViewSet(viewsets.ModelViewSet):
    queryset = House.objects.all()
    serializer_class = HouseSerializer
    lookup_field = 'house_id'
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['name', 'price', 'area', 'bedrooms', 'zone', 'freguesia', 'concelho', 'source', 'scraped_at']
    ordering = ['-scraped_at']  # Default ordering by scraped_at descending

    def get_queryset(self):
        """
        Optionally restricts the returned houses,
        by filtering against query parameters in the URL.
        """
        queryset = House.objects.all()
        
        # Filter out discarded houses if requested
        include_discarded = self.request.query_params.get('include_discarded', 'false').lower() == 'true'
        if not include_discarded:
            queryset = queryset.filter(discarded=False)
            
        # Filter out room rentals based on title terms
        room_rental_filter = Q()
        for term in ROOM_RENTAL_TITLE_TERMS:
            room_rental_filter |= Q(name__icontains=term)
        queryset = queryset.exclude(room_rental_filter)
            
        return queryset

    @action(detail=True, methods=['post'])
    def toggle_contacted(self, request, house_id=None):
        house = self.get_object()
        house.contacted = not house.contacted
        house.save()
        return Response({'contacted': house.contacted})

    @action(detail=True, methods=['post'])
    def toggle_discarded(self, request, house_id=None):
        house = self.get_object()
        house.discarded = not house.discarded
        house.save()
        return Response({'discarded': house.discarded})

    @action(detail=True, methods=['post'])
    def toggle_favorite(self, request, house_id=None):
        house = self.get_object()
        house.favorite = not house.favorite
        house.save()
        return Response({'favorite': house.favorite})

    @action(detail=False, methods=['get'])
    def scraper_status(self, request):
        """Get the status of all scrapers"""
        status_data = {}
        
        # Directory containing scraper status files
        status_dir = Path("data/scraper_status")
        
        # Dynamically find all status files
        if status_dir.exists() and status_dir.is_dir():
            for status_file in status_dir.glob("*_status.json"):
                scraper_name = status_file.stem.replace('_status', '')
                try:
                    with open(status_file, 'r', encoding='utf-8') as f:
                        scraper_data = json.load(f)
                        # Get the most recent status entry
                        if scraper_data and len(scraper_data) > 0:
                            latest = scraper_data[0]  # Assuming the most recent is first
                            # Format the scraper name to be more readable
                            display_name = scraper_name.replace('_', ' ').title()
                            status_data[scraper_name] = {
                                "name": display_name,
                                "status": latest["status"],
                                "timestamp": latest["timestamp"],
                                "houses_processed": latest["houses_processed"],
                                "houses_found": latest["houses_found"],
                                "error_message": latest["error_message"]
                            }
                except Exception as e:
                    # Format the scraper name to be more readable
                    display_name = scraper_name.replace('_', ' ').title()
                    status_data[scraper_name] = {
                        "name": display_name,
                        "status": "error",
                        "timestamp": datetime.now().isoformat(),
                        "houses_processed": 0,
                        "houses_found": 0,
                        "error_message": str(e)
                    }
        
        return Response(status_data)
