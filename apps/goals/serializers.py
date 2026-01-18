from rest_framework import serializers
from .models import Objective, KeyResult


class KeyResultSerializer(serializers.ModelSerializer):
    """Serializer para Key Results."""

    progress = serializers.IntegerField(read_only=True)

    class Meta:
        model = KeyResult
        fields = [
            'id',
            'objective_id',
            'title',
            'current_value',
            'target_value',
            'unit',
            'progress',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'objective_id', 'created_at', 'updated_at']


class LinkedFinanceGoalSerializer(serializers.Serializer):
    """Serializer para la meta financiera vinculada."""

    type = serializers.CharField(source='linked_finance_type')
    target_amount = serializers.DecimalField(
        source='linked_finance_target',
        max_digits=12,
        decimal_places=2
    )
    current_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )


class ObjectiveSerializer(serializers.ModelSerializer):
    """Serializer para Objectives."""

    key_results = KeyResultSerializer(many=True, read_only=True)
    progress = serializers.IntegerField(read_only=True)
    linked_finance_goal = serializers.SerializerMethodField()

    class Meta:
        model = Objective
        fields = [
            'id',
            'title',
            'description',
            'category',
            'status',
            'start_date',
            'end_date',
            'key_results',
            'linked_finance_goal',
            'progress',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_linked_finance_goal(self, obj):
        if obj.linked_finance_type and obj.linked_finance_target:
            return {
                'type': obj.linked_finance_type,
                'target_amount': obj.linked_finance_target,
                'current_amount': 0  # Esto se puede calcular según el tipo
            }
        return None


class ObjectiveCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear Objectives con linked_finance_goal."""

    linked_finance_goal = serializers.DictField(write_only=True, required=False)

    class Meta:
        model = Objective
        fields = [
            'id',
            'title',
            'description',
            'category',
            'status',
            'start_date',
            'end_date',
            'linked_finance_goal',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        linked_finance_goal = validated_data.pop('linked_finance_goal', None)

        if linked_finance_goal:
            validated_data['linked_finance_type'] = linked_finance_goal.get('type')
            validated_data['linked_finance_target'] = linked_finance_goal.get('target_amount')

        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        linked_finance_goal = validated_data.pop('linked_finance_goal', None)

        if linked_finance_goal is not None:
            validated_data['linked_finance_type'] = linked_finance_goal.get('type')
            validated_data['linked_finance_target'] = linked_finance_goal.get('target_amount')

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return ObjectiveSerializer(instance).data


class ObjectiveStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas de objetivos."""

    total = serializers.IntegerField()
    active = serializers.IntegerField()
    completed = serializers.IntegerField()
    paused = serializers.IntegerField()
    average_progress = serializers.IntegerField()
    by_category = serializers.DictField(child=serializers.IntegerField())
