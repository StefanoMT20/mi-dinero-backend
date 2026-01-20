from rest_framework import serializers
from .models import Installment


class InstallmentSerializer(serializers.ModelSerializer):
    """Serializer para Installment."""

    monthly_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    remaining_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Installment
        fields = [
            'id',
            'credit_card',
            'description',
            'total_amount',
            'currency',
            'total_installments',
            'current_installment',
            'monthly_amount',
            'remaining_amount',
            'start_date',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
