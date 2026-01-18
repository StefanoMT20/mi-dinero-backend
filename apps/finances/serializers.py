from rest_framework import serializers
from .models import CreditCard, Expense


class CreditCardSerializer(serializers.ModelSerializer):
    """Serializer para tarjetas de crédito."""

    available = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = CreditCard
        fields = [
            'id',
            'name',
            'last_four_digits',
            'limit',
            'used',
            'available',
            'color',
            'cut_off_date',
            'payment_date',
        ]
        read_only_fields = ['id', 'used', 'available']


class ExpenseSerializer(serializers.ModelSerializer):
    """Serializer para gastos."""

    credit_card_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Expense
        fields = [
            'id',
            'amount',
            'category',
            'description',
            'date',
            'credit_card_id',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        credit_card_id = validated_data.pop('credit_card_id', None)
        user = self.context['request'].user
        validated_data['user'] = user

        if credit_card_id:
            validated_data['credit_card'] = CreditCard.objects.get(id=credit_card_id, user=user)

        return super().create(validated_data)

    def update(self, instance, validated_data):
        credit_card_id = validated_data.pop('credit_card_id', None)
        user = self.context['request'].user

        if credit_card_id is not None:
            if credit_card_id:
                validated_data['credit_card'] = CreditCard.objects.get(id=credit_card_id, user=user)
            else:
                validated_data['credit_card'] = None

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['credit_card_id'] = instance.credit_card_id
        return data


class ExpenseStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas de gastos."""

    monthly_total = serializers.DecimalField(max_digits=12, decimal_places=2)
    by_category = serializers.DictField(child=serializers.DecimalField(max_digits=12, decimal_places=2))
    month = serializers.IntegerField()
    year = serializers.IntegerField()
