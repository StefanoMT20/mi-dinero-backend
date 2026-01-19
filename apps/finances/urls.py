from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import BankAccountViewSet, CreditCardViewSet, ExpenseViewSet

router = DefaultRouter()
router.register(r'bank-accounts', BankAccountViewSet, basename='bank-account')
router.register(r'credit-cards', CreditCardViewSet, basename='credit-card')
router.register(r'expenses', ExpenseViewSet, basename='expense')

urlpatterns = [
    path('', include(router.urls)),
]
