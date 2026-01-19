from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ObjectiveViewSet, KeyResultViewSet, MilestoneViewSet

router = DefaultRouter()
router.register(r'objectives', ObjectiveViewSet, basename='objective')
router.register(r'key-results', KeyResultViewSet, basename='key-result')
router.register(r'milestones', MilestoneViewSet, basename='milestone')

urlpatterns = [
    path('', include(router.urls)),
]
