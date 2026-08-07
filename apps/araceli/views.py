from datetime import date
from decimal import Decimal

from django.db.models import Sum
from rest_framework import viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ClothingItem, ClothingStatus, NailService
from .serializers import ClothingItemSerializer, NailServiceSerializer

ZERO = Decimal('0.00')


def money(value):
    """Decimal -> string con 2 decimales. None cuenta como 0."""
    return str((value or ZERO).quantize(ZERO))


def percent(part, whole):
    """Porcentaje con 1 decimal. Divisor 0/None -> 0.0."""
    if not whole:
        return 0.0
    return round(float(part / whole) * 100, 1)


def sum_of(queryset, field):
    return queryset.aggregate(total=Sum(field))['total'] or ZERO


class AraceliViewSet(viewsets.ModelViewSet):
    """Base: aísla por usuario y acepta multipart para la foto."""

    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        return self.serializer_class.Meta.model.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class NailServiceViewSet(AraceliViewSet):
    serializer_class = NailServiceSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')
        if month:
            queryset = queryset.filter(date__month=month)
        if year:
            queryset = queryset.filter(date__year=year)
        return queryset


class ClothingItemViewSet(AraceliViewSet):
    serializer_class = ClothingItemSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset


class AraceliStatsView(APIView):
    """Resumen mensual de uñas y ropa."""

    def get(self, request):
        today = date.today()
        month = int(request.query_params.get('month') or today.month)
        year = int(request.query_params.get('year') or today.year)

        nails = NailService.objects.filter(
            user=request.user, date__month=month, date__year=year
        )
        count = nails.count()
        revenue = sum_of(nails, 'price')
        cost = sum_of(nails, 'cost')
        profit = revenue - cost

        items = ClothingItem.objects.filter(user=request.user)
        bought = items.filter(purchase_date__month=month, purchase_date__year=year)
        sold = items.filter(
            status=ClothingStatus.SOLD, sale_date__month=month, sale_date__year=year
        )
        invested = sum_of(bought, 'purchase_price')
        sales = sum_of(sold, 'sale_price')
        cost_of_sold = sum_of(sold, 'purchase_price')
        clothing_profit = sales - cost_of_sold
        # ponytail: stock_value es el stock actual, no del mes consultado
        stock_value = sum_of(items.filter(status=ClothingStatus.IN_STOCK), 'purchase_price')

        return Response({
            'nails': {
                'count': count,
                'revenue': money(revenue),
                'cost': money(cost),
                'profit': money(profit),
                'margin_percent': percent(profit, revenue),
                'average_ticket': money(revenue / count if count else ZERO),
            },
            'clothing': {
                'invested': money(invested),
                'sales': money(sales),
                'cost_of_sold': money(cost_of_sold),
                'profit': money(clothing_profit),
                'margin_percent': percent(clothing_profit, sales),
                'roi_percent': percent(clothing_profit, cost_of_sold),
                'stock_value': money(stock_value),
            },
        })
