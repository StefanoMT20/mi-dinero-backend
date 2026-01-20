from rest_framework import serializers
from .models import Budget


class BudgetSerializer(serializers.ModelSerializer):
    """Serializer para Budget."""

    class Meta:
        model = Budget
        fields = [
            'id',
            'category',
            'amount',
            'period',
            'start_date',
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
