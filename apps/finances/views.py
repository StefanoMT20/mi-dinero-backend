from django.db.models import Sum
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import CreditCard, Expense
from .serializers import CreditCardSerializer, ExpenseSerializer, ExpenseStatsSerializer


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
        queryset = Expense.objects.filter(user=self.request.user).select_related('credit_card')

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
            queryset = queryset.filter(category=category)

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
        )

        monthly_total = expenses.aggregate(total=Sum('amount'))['total'] or 0

        by_category = {}
        category_totals = expenses.values('category').annotate(total=Sum('amount'))
        for item in category_totals:
            by_category[item['category']] = item['total']

        data = {
            'monthly_total': monthly_total,
            'by_category': by_category,
            'month': month,
            'year': year,
        }

        serializer = ExpenseStatsSerializer(data)
        return Response(serializer.data)
