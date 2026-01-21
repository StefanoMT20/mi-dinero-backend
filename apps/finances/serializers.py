from rest_framework import serializers
from .models import BankAccount, CreditCard, Expense, Income


class BankAccountSerializer(serializers.ModelSerializer):
    """Serializer para cuentas bancarias."""

    class Meta:
        model = BankAccount
        fields = ['id', 'name', 'balance', 'last_four_digits', 'currency']
        read_only_fields = ['id']


class CreditCardSerializer(serializers.ModelSerializer):
    """Serializer para tarjetas de crédito."""

    class Meta:
        model = CreditCard
        fields = [
            'id',
            'name',
            'last_four_digits',
            'limit',
            'currency',
            'used_pen',
            'used_usd',
            'color',
            'cut_off_date',
            'payment_date',
        ]
        read_only_fields = ['id']


class ExpenseSerializer(serializers.ModelSerializer):
    """Serializer para gastos."""

    credit_card_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    bank_account_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Expense
        fields = [
            'id',
            'amount',
            'currency',
            'category',
            'description',
            'date',
            'credit_card_id',
            'bank_account_id',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        from .models import BankAccount

        credit_card_id = validated_data.pop('credit_card_id', None)
        bank_account_id = validated_data.pop('bank_account_id', None)
        user = self.context['request'].user
        validated_data['user'] = user

        if credit_card_id:
            validated_data['credit_card'] = CreditCard.objects.get(id=credit_card_id, user=user)

        if bank_account_id:
            validated_data['bank_account'] = BankAccount.objects.get(id=bank_account_id, user=user)

        return super().create(validated_data)

    def update(self, instance, validated_data):
        from .models import BankAccount

        credit_card_id = validated_data.pop('credit_card_id', None)
        bank_account_id = validated_data.pop('bank_account_id', None)
        user = self.context['request'].user

        if credit_card_id is not None:
            if credit_card_id:
                validated_data['credit_card'] = CreditCard.objects.get(id=credit_card_id, user=user)
            else:
                validated_data['credit_card'] = None

        if bank_account_id is not None:
            if bank_account_id:
                validated_data['bank_account'] = BankAccount.objects.get(id=bank_account_id, user=user)
            else:
                validated_data['bank_account'] = None

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['credit_card_id'] = instance.credit_card_id
        data['bank_account_id'] = instance.bank_account_id
        return data


class ExpenseStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas de gastos."""

    monthly_total = serializers.DecimalField(max_digits=12, decimal_places=2)
    by_category = serializers.DictField(child=serializers.DecimalField(max_digits=12, decimal_places=2))
    month = serializers.IntegerField()
    year = serializers.IntegerField()


class IncomeSerializer(serializers.ModelSerializer):
    """Serializer para ingresos."""

    bank_account_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Income
        fields = [
            'id',
            'amount',
            'category',
            'description',
            'currency',
            'date',
            'bank_account_id',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        bank_account_id = validated_data.pop('bank_account_id', None)
        user = self.context['request'].user
        validated_data['user'] = user

        if bank_account_id:
            validated_data['bank_account'] = BankAccount.objects.get(id=bank_account_id, user=user)

        return super().create(validated_data)

    def update(self, instance, validated_data):
        bank_account_id = validated_data.pop('bank_account_id', None)
        user = self.context['request'].user

        if bank_account_id is not None:
            if bank_account_id:
                validated_data['bank_account'] = BankAccount.objects.get(id=bank_account_id, user=user)
            else:
                validated_data['bank_account'] = None

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['bank_account_id'] = instance.bank_account_id
        return data
