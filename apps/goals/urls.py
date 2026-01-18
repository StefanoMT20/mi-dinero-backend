from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ObjectiveViewSet, KeyResultViewSet

router = DefaultRouter()
router.register(r'objectives', ObjectiveViewSet, basename='objective')
router.register(r'key-results', KeyResultViewSet, basename='key-result')

urlpatterns = [
    path('', include(router.urls)),
]
