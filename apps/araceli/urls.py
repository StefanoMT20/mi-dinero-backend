from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AraceliStatsView, ClothingItemViewSet, NailServiceViewSet

router = DefaultRouter()
router.register(r'nail-services', NailServiceViewSet, basename='nail-service')
router.register(r'clothing-items', ClothingItemViewSet, basename='clothing-item')

urlpatterns = [
    path('stats/', AraceliStatsView.as_view(), name='araceli-stats'),
    path('', include(router.urls)),
]
