from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from houses.views import HouseViewSet

router = routers.DefaultRouter()
router.register(r'houses', HouseViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/scraper-status/', HouseViewSet.as_view({'get': 'scraper_status'}), name='scraper-status'),
    path('api/run-scrapers/', HouseViewSet.as_view({'post': 'run_scrapers'}), name='run-scrapers'),
] 