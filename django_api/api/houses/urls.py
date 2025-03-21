from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HouseViewSet

router = DefaultRouter()
router.register(r'houses', HouseViewSet, basename='house')

urlpatterns = [
    path('', include(router.urls)),
    path('scraper-status/', HouseViewSet.as_view({'get': 'scraper_status'}), name='scraper-status'),
    path('run-scrapers/', HouseViewSet.as_view({'post': 'run_scrapers'}), name='run-scrapers'),
] 