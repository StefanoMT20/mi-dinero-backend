from rest_framework import serializers
from apps.categories.models import Category
from .models import BankAccount, CreditCard, Expense, FixedExpense, FixedIncome, Income


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

    category = serializers.UUIDField()
    credit_card_id = serializers.UUIDField(required=False, allow_null=True)
    bank_account_id = serializers.UUIDField(required=False, allow_null=True)

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
        credit_card_id = validated_data.pop('credit_card_id', None)
        bank_account_id = validated_data.pop('bank_account_id', None)
        category_id = validated_data.pop('category')
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
        credit_card_id = validated_data.pop('credit_card_id', None)
        bank_account_id = validated_data.pop('bank_account_id', None)
        category_id = validated_data.pop('category', None)
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
        data['category'] = str(instance.category_id) if instance.category_id else None
        data['credit_card_id'] = str(instance.credit_card_id) if instance.credit_card_id else None
        data['bank_account_id'] = str(instance.bank_account_id) if instance.bank_account_id else None
        return data


class ExpenseStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas de gastos."""

    monthly_total = serializers.DecimalField(max_digits=12, decimal_places=2)
    by_category = serializers.DictField(child=serializers.DecimalField(max_digits=12, decimal_places=2))
    month = serializers.IntegerField()
    year = serializers.IntegerField()


class IncomeSerializer(serializers.ModelSerializer):
    """Serializer para ingresos."""

    category = serializers.UUIDField()
    bank_account_id = serializers.UUIDField(required=False, allow_null=True)

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
        category_id = validated_data.pop('category')
        user = self.context['request'].user
        validated_data['user'] = user

        # Buscar categoría del usuario
        validated_data['category'] = Category.objects.get(id=category_id, user=user)

        if bank_account_id:
            validated_data['bank_account'] = BankAccount.objects.get(id=bank_account_id, user=user)

        return super().create(validated_data)

    def update(self, instance, validated_data):
        bank_account_id = validated_data.pop('bank_account_id', None)
        category_id = validated_data.pop('category', None)
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
        data['category'] = str(instance.category_id) if instance.category_id else None
        data['bank_account_id'] = str(instance.bank_account_id) if instance.bank_account_id else None
        return data


class FixedExpenseSerializer(serializers.ModelSerializer):
    """Serializer para gastos fijos."""

    category = serializers.UUIDField()
    credit_card_id = serializers.UUIDField(required=False, allow_null=True)
    bank_account_id = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = FixedExpense
        fields = [
            'id',
            'name',
            'amount',
            'currency',
            'category',
            'day_of_month',
            'credit_card_id',
            'bank_account_id',
            'is_active',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        credit_card_id = validated_data.pop('credit_card_id', None)
        bank_account_id = validated_data.pop('bank_account_id', None)
        category_id = validated_data.pop('category')
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
        credit_card_id = validated_data.pop('credit_card_id', None)
        bank_account_id = validated_data.pop('bank_account_id', None)
        category_id = validated_data.pop('category', None)
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
        data['category'] = str(instance.category_id) if instance.category_id else None
        data['credit_card_id'] = str(instance.credit_card_id) if instance.credit_card_id else None
        data['bank_account_id'] = str(instance.bank_account_id) if instance.bank_account_id else None
        return data


class FixedIncomeSerializer(serializers.ModelSerializer):
    """Serializer para ingresos fijos."""

    category = serializers.UUIDField()
    bank_account_id = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = FixedIncome
        fields = [
            'id',
            'name',
            'amount',
            'currency',
            'category',
            'day_of_month',
            'bank_account_id',
            'is_active',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        bank_account_id = validated_data.pop('bank_account_id', None)
        category_id = validated_data.pop('category')
        user = self.context['request'].user
        validated_data['user'] = user

        # Buscar categoría del usuario
        validated_data['category'] = Category.objects.get(id=category_id, user=user)

        if bank_account_id:
            validated_data['bank_account'] = BankAccount.objects.get(id=bank_account_id, user=user)

        return super().create(validated_data)

    def update(self, instance, validated_data):
        bank_account_id = validated_data.pop('bank_account_id', None)
        category_id = validated_data.pop('category', None)
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
        data['category'] = str(instance.category_id) if instance.category_id else None
        data['bank_account_id'] = str(instance.bank_account_id) if instance.bank_account_id else None
        return data
