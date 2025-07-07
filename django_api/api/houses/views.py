from django.shortcuts import render
from rest_framework import viewsets, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import House, MainRun
from .serializers import HouseSerializer
from .settings import ROOM_RENTAL_TITLE_TERMS
import json
from pathlib import Path
from datetime import datetime


class HouseViewSet(viewsets.ModelViewSet):
    serializer_class = HouseSerializer
    pagination_class = None  # Disable pagination
    lookup_field = 'house_id'
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['name', 'price', 'area_str', 'bedrooms', 'zone', 'freguesia', 'concelho', 'source', 'scraped_at']
    ordering = ['-scraped_at']
    # permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Restricts the returned houses by filtering against query parameters in the URL
        and user-specific filters.
        """
        queryset = House.objects.all()
        
        # Clean up image URLs by removing duplicates while preserving extensions
        for house in queryset:
            if house.image_urls:
                urls = house.image_urls.split('|||')
                unique_urls = {}
                for url in urls:
                    base_url = url.rsplit('.', 1)[0]
                    extension = url.rsplit('.', 1)[1] if '.' in url else ''
                    if base_url not in unique_urls or extension == 'webp':
                        unique_urls[base_url] = url
                house.image_urls = '|||'.join(unique_urls.values())
                house.save()
        
        # Filter out houses discarded by the current user
        if self.request.user.is_authenticated:
            queryset = queryset.exclude(discarded_by=self.request.user)
            
        # Filter out room rentals based on title terms
        room_rental_filter = Q()
        for term in ROOM_RENTAL_TITLE_TERMS:
            room_rental_filter |= Q(name__icontains=term)
        queryset = queryset.exclude(room_rental_filter)

        # Handle additional filters
        show_favorites = self.request.query_params.get('favorites', '').lower() == 'true'
        show_contacted = self.request.query_params.get('contacted', '').lower() == 'true'

        if show_favorites:
            queryset = queryset.filter(favorited_by=self.request.user)
        if show_contacted:
            queryset = queryset.filter(contacted_by=self.request.user)
            
        return queryset

    @action(detail=True, methods=['post'])
    def toggle_contacted(self, request, house_id=None):
        house = self.get_object()
        if house.contacted_by.filter(id=request.user.id).exists():
            house.contacted_by.remove(request.user)
            is_contacted = False
        else:
            house.contacted_by.add(request.user)
            is_contacted = True
        return Response({'is_contacted': is_contacted})

    @action(detail=True, methods=['post'])
    def toggle_discarded(self, request, house_id=None):
        try:
            house = House.objects.get(house_id=house_id)
            if house.discarded_by.filter(id=request.user.id).exists():
                house.discarded_by.remove(request.user)
                is_discarded = False
            else:
                house.discarded_by.add(request.user)
                is_discarded = True
            return Response({'is_discarded': is_discarded})
        except House.DoesNotExist:
            return Response({'error': 'House not found'}, status=404)

    @action(detail=True, methods=['post'])
    def toggle_favorite(self, request, house_id=None):
        house = self.get_object()
        if house.favorited_by.filter(id=request.user.id).exists():
            house.favorited_by.remove(request.user)
            is_favorite = False
        else:
            house.favorited_by.add(request.user)
            is_favorite = True
        return Response({'is_favorite': is_favorite})

    @action(detail=False, methods=['get'])
    def scraper_status(self, request):
        """Get the status of all scrapers"""
        status_data = {
            "main_run": {
                "status": None,
                "start_time": None,
                "end_time": None,
                "total_houses": 0,
                "new_houses": 0,
                "error_message": None
            },
            "scrapers": {}
        }
        
        # Get the most recent main run
        try:
            main_run = MainRun.objects.order_by('-start_time').first()
            print(f"Main run fields:")
            print(f"Status: {main_run.status}")
            print(f"Start time: {main_run.start_time}")
            print(f"End time: {main_run.end_time}")
            print(f"Total houses: {main_run.total_houses}")
            print(f"New houses: {main_run.new_houses}")
            print(f"Error message: {main_run.error_message}")
            print("---")
            
            if main_run:
                # Update main run status
                status_data["main_run"] = {
                    "status": main_run.status,
                    "start_time": main_run.start_time.isoformat() if main_run.start_time else None,
                    "end_time": main_run.end_time.isoformat() if main_run.end_time else None,
                    "total_houses": main_run.total_houses,
                    "new_houses": main_run.new_houses,
                    "error_message": main_run.error_message,
                    "last_run_date": MainRun.objects.exclude(id=main_run.id).order_by('-start_time').values_list('start_time', flat=True).first().isoformat() if MainRun.objects.exclude(id=main_run.id).exists() else None
                }
                
                # Get all scraper runs associated with this main run
                scraper_runs = main_run.scraper_runs.all()
                
                for run in scraper_runs:
                    # Format the scraper name to be more readable
                    display_name = run.scraper.replace('_', ' ').title()
                    status_data["scrapers"][run.scraper] = {
                        "name": display_name,
                        "status": run.status,
                        "timestamp": run.start_time.isoformat(),
                        "houses_processed": run.total_houses,
                        "houses_found": run.new_houses,
                        "error_message": run.error_message
                    }
        except Exception as e:
            print(f"Error in scraper_status: {str(e)}")
            # If there's an error, we'll return the default status_data
            pass
        
        return Response(status_data)

    @action(detail=False, methods=['post'])
    def run_scrapers(self, request):
        """Trigger the run_scrapers management command"""
        from django.core.management import call_command
        import io
        
        # Capture the output of the command
        out = io.StringIO()
        try:
            call_command('run_scrapers', '--force', stdout=out)
            return Response({'status': 'success', 'output': out.getvalue()})
        except Exception as e:
            
            print(f"Error running scrapers: {e}")
            return Response({'status': 'error', 'error': str(e)}, status=500)
