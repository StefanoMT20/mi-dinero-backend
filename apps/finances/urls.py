from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import BankAccountViewSet, CreditCardViewSet, ExpenseViewSet, FixedExpenseViewSet, IncomeViewSet

router = DefaultRouter()
router.register(r'bank-accounts', BankAccountViewSet, basename='bank-account')
router.register(r'credit-cards', CreditCardViewSet, basename='credit-card')
router.register(r'expenses', ExpenseViewSet, basename='expense')
router.register(r'incomes', IncomeViewSet, basename='income')
router.register(r'fixed-expenses', FixedExpenseViewSet, basename='fixed-expense')

urlpatterns = [
    path('', include(router.urls)),
]
