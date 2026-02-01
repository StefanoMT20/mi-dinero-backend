from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import BankAccount, CreditCard, CreditCardPayment, Expense, FixedExpense, FixedIncome, Income
from .serializers import (
    BankAccountSerializer,
    CreditCardSerializer,
    CreditCardPaymentSerializer,
    ExpenseSerializer,
    ExpenseStatsSerializer,
    FixedExpenseSerializer,
    FixedIncomeSerializer,
    IncomeSerializer,
)


class BankAccountViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar cuentas bancarias."""

    serializer_class = BankAccountSerializer

    def get_queryset(self):
        return BankAccount.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def deduct(self, request, pk=None):
        """Deducir monto del balance."""
        account = self.get_object()
        amount = request.data.get('amount', 0)

        try:
            amount = Decimal(str(amount))
        except (ValueError, TypeError):
            return Response(
                {'error': 'El monto debe ser un número válido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if amount <= 0:
            return Response(
                {'error': 'El monto debe ser mayor a 0'},
                status=status.HTTP_400_BAD_REQUEST
            )

        account.balance -= amount
        account.save()

        serializer = self.get_serializer(account)
        return Response(serializer.data)


class CreditCardViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar tarjetas de crédito."""

    serializer_class = CreditCardSerializer

    def get_queryset(self):
        return CreditCard.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ExpenseViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar gastos."""

    serializer_class = ExpenseSerializer

    def get_queryset(self):
        queryset = Expense.objects.filter(user=self.request.user).select_related('credit_card', 'category')

        # Filtros
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')
        category = self.request.query_params.get('category')
        credit_card_id = self.request.query_params.get('credit_card_id')

        if month and year:
            queryset = queryset.filter(date__month=month, date__year=year)
        elif year:
            queryset = queryset.filter(date__year=year)

        if category:
            queryset = queryset.filter(category_id=category)

        if credit_card_id:
            queryset = queryset.filter(credit_card_id=credit_card_id)

        return queryset

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Estadísticas de gastos del mes actual o especificado."""
        now = timezone.now()
        month = int(request.query_params.get('month', now.month))
        year = int(request.query_params.get('year', now.year))

        expenses = Expense.objects.filter(
            user=request.user,
            date__month=month,
            date__year=year
        ).select_related('category')

        monthly_total = expenses.aggregate(total=Sum('amount'))['total'] or 0

        by_category = {}
        category_totals = expenses.values('category__id', 'category__name').annotate(total=Sum('amount'))
        for item in category_totals:
            by_category[item['category__name']] = item['total']

        data = {
            'monthly_total': monthly_total,
            'by_category': by_category,
            'month': month,
            'year': year,
        }

        serializer = ExpenseStatsSerializer(data)
        return Response(serializer.data)


class IncomeViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar ingresos."""

    serializer_class = IncomeSerializer

    def get_queryset(self):
        queryset = Income.objects.filter(user=self.request.user).select_related('bank_account', 'category')

        # Filtros
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')
        category = self.request.query_params.get('category')
        bank_account_id = self.request.query_params.get('bank_account_id')

        if month and year:
            queryset = queryset.filter(date__month=month, date__year=year)
        elif year:
            queryset = queryset.filter(date__year=year)

        if category:
            queryset = queryset.filter(category_id=category)

        if bank_account_id:
            queryset = queryset.filter(bank_account_id=bank_account_id)

        return queryset


class FixedExpenseViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar gastos fijos."""

    serializer_class = FixedExpenseSerializer

    def get_queryset(self):
        return FixedExpense.objects.filter(user=self.request.user).select_related(
            'credit_card', 'bank_account', 'category'
        )

    @action(detail=False, methods=['post'])
    def process_pending(self, request):
        """Convierte gastos fijos pendientes en gastos reales."""
        today = timezone.now().date()
        current_month_start = today.replace(day=1)

        # Buscar gastos fijos que:
        # 1. Estén activos
        # 2. Su día del mes ya pasó o es hoy
        # 3. No se hayan procesado este mes
        pending_fixed = FixedExpense.objects.filter(
            user=request.user,
            is_active=True,
            day_of_month__lte=today.day
        ).exclude(
            last_processed_date__gte=current_month_start
        )

        created_expenses = []
        for fixed in pending_fixed:
            # Crear el gasto real
            expense_date = today.replace(day=min(fixed.day_of_month, today.day))
            expense = Expense.objects.create(
                user=request.user,
                amount=fixed.amount,
                currency=fixed.currency,
                category=fixed.category,
                description=f"{fixed.name} (Fijo)",
                date=expense_date,
                credit_card=fixed.credit_card,
                bank_account=fixed.bank_account,
            )
            created_expenses.append(expense.id)

            # Marcar como procesado
            fixed.last_processed_date = today
            fixed.save(update_fields=['last_processed_date'])

        return Response({
            'processed': len(created_expenses),
            'expense_ids': [str(id) for id in created_expenses]
        })


class FixedIncomeViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar ingresos fijos."""

    serializer_class = FixedIncomeSerializer

    def get_queryset(self):
        return FixedIncome.objects.filter(user=self.request.user).select_related(
            'bank_account', 'category'
        )

    @action(detail=False, methods=['post'])
    def process_pending(self, request):
        """Convierte ingresos fijos pendientes en ingresos reales."""
        today = timezone.now().date()
        current_month_start = today.replace(day=1)

        # Buscar ingresos fijos que:
        # 1. Estén activos
        # 2. Su día del mes ya pasó o es hoy
        # 3. No se hayan procesado este mes
        pending_fixed = FixedIncome.objects.filter(
            user=request.user,
            is_active=True,
            day_of_month__lte=today.day
        ).exclude(
            last_processed_date__gte=current_month_start
        )

        created_incomes = []
        for fixed in pending_fixed:
            # Crear el ingreso real
            income_date = today.replace(day=min(fixed.day_of_month, today.day))
            income = Income.objects.create(
                user=request.user,
                amount=fixed.amount,
                currency=fixed.currency,
                category=fixed.category,
                description=f"{fixed.name} (Fijo)",
                date=income_date,
                bank_account=fixed.bank_account,
            )
            created_incomes.append(income.id)

            # Marcar como procesado
            fixed.last_processed_date = today
            fixed.save(update_fields=['last_processed_date'])

        return Response({
            'processed': len(created_incomes),
            'income_ids': [str(id) for id in created_incomes]
        })


class CreditCardPaymentViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar pagos de tarjetas de crédito."""

    serializer_class = CreditCardPaymentSerializer

    def get_queryset(self):
        queryset = CreditCardPayment.objects.filter(user=self.request.user).select_related(
            'credit_card', 'bank_account'
        )

        # Filtros
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')
        credit_card_id = self.request.query_params.get('credit_card_id')

        if month and year:
            queryset = queryset.filter(date__month=month, date__year=year)
        elif year:
            queryset = queryset.filter(date__year=year)

        if credit_card_id:
            queryset = queryset.filter(credit_card_id=credit_card_id)

        return queryset
