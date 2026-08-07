from decimal import Decimal

from django.test import SimpleTestCase

from .views import money, percent


class MoneyMathTests(SimpleTestCase):
    def test_money_formats_two_decimals(self):
        self.assertEqual(money(Decimal('180000')), '180000.00')
        self.assertEqual(money(Decimal('15000.456')), '15000.46')
        self.assertEqual(money(None), '0.00')

    def test_percent_one_decimal(self):
        self.assertEqual(percent(Decimal('138000'), Decimal('180000')), 76.7)
        self.assertEqual(percent(Decimal('110000'), Decimal('200000')), 55.0)

    def test_percent_zero_divisor(self):
        self.assertEqual(percent(Decimal('0'), Decimal('0')), 0.0)
        self.assertEqual(percent(Decimal('100'), None), 0.0)
