from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CreditCardViewSet, ExpenseViewSet

router = DefaultRouter()
router.register(r'credit-cards', CreditCardViewSet, basename='credit-card')
router.register(r'expenses', ExpenseViewSet, basename='expense')

urlpatterns = [
    path('', include(router.urls)),
]
