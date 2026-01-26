from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import BankAccountViewSet, CreditCardViewSet, ExpenseViewSet, FixedExpenseViewSet, FixedIncomeViewSet, IncomeViewSet

router = DefaultRouter()
router.register(r'bank-accounts', BankAccountViewSet, basename='bank-account')
router.register(r'credit-cards', CreditCardViewSet, basename='credit-card')
router.register(r'expenses', ExpenseViewSet, basename='expense')
router.register(r'incomes', IncomeViewSet, basename='income')
router.register(r'fixed-expenses', FixedExpenseViewSet, basename='fixed-expense')
router.register(r'fixed-incomes', FixedIncomeViewSet, basename='fixed-income')

urlpatterns = [
    path('', include(router.urls)),
]
