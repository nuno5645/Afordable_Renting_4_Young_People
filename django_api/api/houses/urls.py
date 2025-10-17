from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HouseViewSet, DistrictViewSet, CountyViewSet, ParishViewSet

router = DefaultRouter()
router.register(r'houses', HouseViewSet, basename='house')
router.register(r'districts', DistrictViewSet, basename='district')
router.register(r'counties', CountyViewSet, basename='county')
router.register(r'parishes', ParishViewSet, basename='parish')

urlpatterns = [
    path('', include(router.urls)),
    path('scraper-status/', HouseViewSet.as_view({'get': 'scraper_status'}), name='scraper-status'),
    path('run-scrapers/', HouseViewSet.as_view({'post': 'run_scrapers'}), name='run-scrapers'),
] 