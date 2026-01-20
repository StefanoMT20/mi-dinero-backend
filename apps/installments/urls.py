from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InstallmentViewSet

router = DefaultRouter()
router.register(r'installments', InstallmentViewSet, basename='installment')

urlpatterns = [
    path('', include(router.urls)),
]
