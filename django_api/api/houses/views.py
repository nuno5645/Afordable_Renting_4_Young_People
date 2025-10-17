from django.shortcuts import render
from rest_framework import viewsets, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import House, MainRun, District, County, Parish
from .serializers import HouseSerializer, DistrictSerializer, CountySerializer, ParishSerializer, MainRunSerializer
from .settings import ROOM_RENTAL_TITLE_TERMS
import json
from pathlib import Path
from datetime import datetime


class HouseViewSet(viewsets.ModelViewSet):
    serializer_class = HouseSerializer
    lookup_field = 'house_id'
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['name', 'price', 'area', 'bedrooms', 'zone', 'freguesia', 'concelho', 'source', 'scraped_at']
    ordering = ['-scraped_at']
    # permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Restricts the returned houses by filtering against query parameters in the URL
        and user-specific filters.
        """
        queryset = House.objects.all()
        
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
        
        # Location filters
        district_id = self.request.query_params.get('district')
        county_id = self.request.query_params.get('county')
        parish_id = self.request.query_params.get('parish')
        source = self.request.query_params.get('source')
        
        if district_id:
            queryset = queryset.filter(district_id=district_id)
        if county_id:
            queryset = queryset.filter(county_id=county_id)
        if parish_id:
            queryset = queryset.filter(parish_id=parish_id)
        if source:
            queryset = queryset.filter(source=source)
        
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
    def stats(self, request):
        """
        Get statistics about houses in the database
        
        Returns:
        {
            "total_houses": 1234,
            "average_price": 850.50
        }
        """
        from django.db.models import Avg, Count
        
        queryset = self.get_queryset()
        
        # Calculate statistics
        stats = queryset.aggregate(
            total_houses=Count('house_id'),
            average_price=Avg('price')
        )

        
        return Response({
            'total_houses': stats['total_houses'] or 0,
            'average_price': float(stats['average_price']) if stats['average_price'] else 0.0
        })

    @action(detail=False, methods=['post'])
    def delete_all(self, request):
        """
        Delete all houses from the database
        
        This will cascade delete all related data including:
        - Photos (due to ForeignKey with on_delete=CASCADE)
        - Many-to-Many relationships (favorited_by, contacted_by, discarded_by)
        
        Returns:
        {
            "status": "success",
            "deleted_count": 1234,
            "message": "Successfully deleted 1234 houses and related data"
        }
        """
        try:
            # Get count before deletion
            house_count = House.objects.count()
            
            # Delete all houses (cascades to photos and clears M2M relationships)
            deleted_info = House.objects.all().delete()
            
            return Response({
                'status': 'success',
                'deleted_count': house_count,
                'deleted_objects': deleted_info[0],  # Total number of objects deleted (houses + photos + m2m)
                'message': f'Successfully deleted {house_count} houses and related data'
            })
            
        except Exception as e:
            print(f"Error deleting all houses: {str(e)}")
            return Response({
                'status': 'error',
                'error': str(e)
            }, status=500)

    @action(detail=False, methods=['post'])
    def run_scrapers(self, request):
        """
        Trigger the run_scrapers management command
        
        Request body (optional):
        {
            "scrapers": ["ImoVirtual", "Idealista", "SuperCasa"],  // Optional: specific scrapers to run
            "all": true  // Optional: run all scrapers (default if no scrapers specified)
        }
        
        Available scrapers:
        - ImoVirtual
        - Idealista
        - Remax
        - ERA
        - CasaSapo
        - SuperCasa
        """
        from django.core.management import call_command
        import io
        
        # Get scrapers selection from request body
        scrapers = request.data.get('scrapers', [])
        run_all = request.data.get('all', False)
        
        # Validate scraper names
        valid_scrapers = ['ImoVirtual', 'Idealista', 'Remax', 'ERA', 'CasaSapo', 'SuperCasa']
        
        if scrapers:
            # Validate that all requested scrapers are valid
            invalid_scrapers = [s for s in scrapers if s not in valid_scrapers]
            if invalid_scrapers:
                return Response({
                    'status': 'error',
                    'error': f'Invalid scrapers: {", ".join(invalid_scrapers)}',
                    'valid_scrapers': valid_scrapers
                }, status=400)
        
        # Capture the output of the command
        out = io.StringIO()
        try:
            # Build command arguments
            cmd_args = []
            
            if run_all or not scrapers:
                # Run all scrapers if explicitly requested or no specific scrapers provided
                cmd_args.append('--all')
            else:
                # Run specific scrapers
                cmd_args.extend(['--scrapers'] + scrapers)
            
            call_command('run_scrapers', *cmd_args, stdout=out)
            
            return Response({
                'status': 'success',
                'output': out.getvalue(),
                'scrapers_run': scrapers if scrapers else 'all',
                'message': f'Started {"all scrapers" if (run_all or not scrapers) else ", ".join(scrapers)}'
            })
        except Exception as e:
            print(f"Error running scrapers: {e}")
            return Response({
                'status': 'error',
                'error': str(e)
            }, status=500)


class DistrictViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing districts.
    Supports filtering by name.
    """
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']
    pagination_class = None  # Disable pagination for location endpoints

    @action(detail=True, methods=['get'])
    def counties(self, request, pk=None):
        """Get all counties in this district"""
        district = self.get_object()
        counties = district.counties.all()
        serializer = CountySerializer(counties, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def houses(self, request, pk=None):
        """Get all houses in this district"""
        district = self.get_object()
        houses = House.objects.filter(district=district)
        
        # Apply pagination
        page = self.paginate_queryset(houses)
        if page is not None:
            serializer = HouseSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = HouseSerializer(houses, many=True, context={'request': request})
        return Response(serializer.data)


class CountyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing counties.
    Supports filtering by name and district.
    """
    queryset = County.objects.all()
    serializer_class = CountySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'district__name']
    ordering_fields = ['name', 'district__name']
    ordering = ['name']
    pagination_class = None  # Disable pagination for location endpoints

    def get_queryset(self):
        queryset = County.objects.all()
        district_id = self.request.query_params.get('district')
        if district_id:
            queryset = queryset.filter(district_id=district_id)
        return queryset

    @action(detail=True, methods=['get'])
    def parishes(self, request, pk=None):
        """Get all parishes in this county"""
        county = self.get_object()
        parishes = county.parishes.all()
        serializer = ParishSerializer(parishes, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def houses(self, request, pk=None):
        """Get all houses in this county"""
        county = self.get_object()
        houses = House.objects.filter(county=county)
        
        # Apply pagination
        page = self.paginate_queryset(houses)
        if page is not None:
            serializer = HouseSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = HouseSerializer(houses, many=True, context={'request': request})
        return Response(serializer.data)


class ParishViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing parishes.
    Supports filtering by name, county, and district.
    """
    queryset = Parish.objects.all()
    serializer_class = ParishSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'county__name', 'county__district__name']
    ordering_fields = ['name', 'county__name']
    ordering = ['name']
    pagination_class = None  # Disable pagination for location endpoints

    def get_queryset(self):
        queryset = Parish.objects.all()
        county_id = self.request.query_params.get('county')
        district_id = self.request.query_params.get('district')
        
        if county_id:
            queryset = queryset.filter(county_id=county_id)
        if district_id:
            queryset = queryset.filter(county__district_id=district_id)
        
        return queryset

    @action(detail=True, methods=['get'])
    def houses(self, request, pk=None):
        """Get all houses in this parish"""
        parish = self.get_object()
        houses = House.objects.filter(parish=parish)
        
        # Apply pagination
        page = self.paginate_queryset(houses)
        if page is not None:
            serializer = HouseSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = HouseSerializer(houses, many=True, context={'request': request})
        return Response(serializer.data)


class MainRunViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for viewing main scraper runs with nested scraper runs.
    
    list: Returns paginated main runs with nested scraper runs
    retrieve: Returns a single main run with its scraper runs
    """
    queryset = MainRun.objects.prefetch_related('scraper_runs').order_by('-start_time')
    serializer_class = MainRunSerializer
    # permission_classes = [permissions.IsAuthenticated]
