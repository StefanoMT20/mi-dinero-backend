from rest_framework import serializers
from apps.categories.models import Category
from apps.categories.serializers import CategorySerializer
from .models import BankAccount, CreditCard, Expense, FixedExpense, Income


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
    category_id = serializers.UUIDField(write_only=True, required=True)

    class Meta:
        model = Expense
        fields = [
            'id',
            'amount',
            'currency',
            'category',
            'category_id',
            'description',
            'date',
            'credit_card_id',
            'bank_account_id',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at', 'category']

    def create(self, validated_data):
        from .models import BankAccount

        credit_card_id = validated_data.pop('credit_card_id', None)
        bank_account_id = validated_data.pop('bank_account_id', None)
        category_id = validated_data.pop('category_id')
        user = self.context['request'].user
        validated_data['user'] = user

        # Buscar categoría del usuario
        validated_data['category'] = Category.objects.get(id=category_id, user=user)

        if credit_card_id:
            validated_data['credit_card'] = CreditCard.objects.get(id=credit_card_id, user=user)

        if bank_account_id:
            validated_data['bank_account'] = BankAccount.objects.get(id=bank_account_id, user=user)

        return super().create(validated_data)

    def update(self, instance, validated_data):
        from .models import BankAccount

        credit_card_id = validated_data.pop('credit_card_id', None)
        bank_account_id = validated_data.pop('bank_account_id', None)
        category_id = validated_data.pop('category_id', None)
        user = self.context['request'].user

        if category_id is not None:
            validated_data['category'] = Category.objects.get(id=category_id, user=user)

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
        data['category'] = CategorySerializer(instance.category).data if instance.category else None
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
    category_id = serializers.UUIDField(write_only=True, required=True)

    class Meta:
        model = Income
        fields = [
            'id',
            'amount',
            'category',
            'category_id',
            'description',
            'currency',
            'date',
            'bank_account_id',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at', 'category']

    def create(self, validated_data):
        bank_account_id = validated_data.pop('bank_account_id', None)
        category_id = validated_data.pop('category_id')
        user = self.context['request'].user
        validated_data['user'] = user

        # Buscar categoría del usuario
        validated_data['category'] = Category.objects.get(id=category_id, user=user)

        if bank_account_id:
            validated_data['bank_account'] = BankAccount.objects.get(id=bank_account_id, user=user)

        return super().create(validated_data)

    def update(self, instance, validated_data):
        bank_account_id = validated_data.pop('bank_account_id', None)
        category_id = validated_data.pop('category_id', None)
        user = self.context['request'].user

        if category_id is not None:
            validated_data['category'] = Category.objects.get(id=category_id, user=user)

        if bank_account_id is not None:
            if bank_account_id:
                validated_data['bank_account'] = BankAccount.objects.get(id=bank_account_id, user=user)
            else:
                validated_data['bank_account'] = None

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['bank_account_id'] = instance.bank_account_id
        data['category'] = CategorySerializer(instance.category).data if instance.category else None
        return data


class FixedExpenseSerializer(serializers.ModelSerializer):
    """Serializer para gastos fijos."""

    credit_card = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    bank_account = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    category_id = serializers.UUIDField(write_only=True, required=True)

    class Meta:
        model = FixedExpense
        fields = [
            'id',
            'name',
            'amount',
            'currency',
            'category',
            'category_id',
            'day_of_month',
            'credit_card',
            'bank_account',
            'is_active',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at', 'category']

    def create(self, validated_data):
        credit_card_id = validated_data.pop('credit_card', None)
        bank_account_id = validated_data.pop('bank_account', None)
        category_id = validated_data.pop('category_id')
        user = self.context['request'].user
        validated_data['user'] = user

        # Buscar categoría del usuario
        validated_data['category'] = Category.objects.get(id=category_id, user=user)

        if credit_card_id:
            validated_data['credit_card'] = CreditCard.objects.get(id=credit_card_id, user=user)

        if bank_account_id:
            validated_data['bank_account'] = BankAccount.objects.get(id=bank_account_id, user=user)

        return super().create(validated_data)

    def update(self, instance, validated_data):
        credit_card_id = validated_data.pop('credit_card', None)
        bank_account_id = validated_data.pop('bank_account', None)
        category_id = validated_data.pop('category_id', None)
        user = self.context['request'].user

        if category_id is not None:
            validated_data['category'] = Category.objects.get(id=category_id, user=user)

        if 'credit_card' in self.initial_data:
            if credit_card_id:
                validated_data['credit_card'] = CreditCard.objects.get(id=credit_card_id, user=user)
            else:
                validated_data['credit_card'] = None

        if 'bank_account' in self.initial_data:
            if bank_account_id:
                validated_data['bank_account'] = BankAccount.objects.get(id=bank_account_id, user=user)
            else:
                validated_data['bank_account'] = None

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['credit_card'] = instance.credit_card_id
        data['bank_account'] = instance.bank_account_id
        data['category'] = CategorySerializer(instance.category).data if instance.category else None
        return data
