from rest_framework import serializers
from apps.categories.models import Category
from .models import Budget


class BudgetSerializer(serializers.ModelSerializer):
    """Serializer para Budget."""

    category = serializers.UUIDField()

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
        category_id = validated_data.pop('category')
        user = self.context['request'].user

        # Buscar categoría del usuario
        validated_data['category'] = Category.objects.get(id=category_id, user=user)
        validated_data['user'] = user

        return super().create(validated_data)

    def update(self, instance, validated_data):
        category_id = validated_data.pop('category', None)
        user = self.context['request'].user

        if category_id is not None:
            validated_data['category'] = Category.objects.get(id=category_id, user=user)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['category'] = str(instance.category_id) if instance.category_id else None
        return data
