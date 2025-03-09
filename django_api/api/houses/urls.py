from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HouseViewSet

router = DefaultRouter()
router.register(r'houses', HouseViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 