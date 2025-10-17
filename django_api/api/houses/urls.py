from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HouseViewSet, DistrictViewSet, CountyViewSet, MainRunViewSet, ParishViewSet

router = DefaultRouter()
router.register(r'houses', HouseViewSet, basename='house')
router.register(r'districts', DistrictViewSet, basename='district')
router.register(r'counties', CountyViewSet, basename='county')
router.register(r'parishes', ParishViewSet, basename='parish')
router.register(r'main-runs', MainRunViewSet, basename='mainrun')

urlpatterns = [
    path('', include(router.urls)),
    path('run-scrapers/', HouseViewSet.as_view({'post': 'run_scrapers'}), name='run-scrapers'),
] 