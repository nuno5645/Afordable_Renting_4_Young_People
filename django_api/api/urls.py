from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from houses.views import HouseViewSet, MainRunViewSet

router = routers.DefaultRouter()
router.register(r'houses', HouseViewSet)
router.register(r'main-runs', MainRunViewSet, basename='mainrun')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/run-scrapers/', HouseViewSet.as_view({'post': 'run_scrapers'}), name='run-scrapers'),
] 