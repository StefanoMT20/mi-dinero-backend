from rest_framework import viewsets
from .models import Installment
from .serializers import InstallmentSerializer


class InstallmentViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar Cuotas."""

    serializer_class = InstallmentSerializer

    def get_queryset(self):
        return Installment.objects.filter(
            user=self.request.user
        ).select_related('credit_card')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
