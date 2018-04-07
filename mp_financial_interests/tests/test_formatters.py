import datetime
import unittest
from mp_financial_interests.lib.formatters import currency_to_float


class TestRegisterIndex(unittest.TestCase):

    def test_currency_formatter_can_handle_commas(self):
        self._format_currency('£1,000', 1000)

    def test_currency_formatter_can_handle_decimals(self):
        self._format_currency('£1,000.69', 1000.69)

    def test_currency_formatter_can_handle_multiple_decimals(self):
        self._format_currency('£1.000.69', 1000.69)

    def _format_currency(self, currency, expected_float):
        self.assertEqual(currency_to_float(currency), expected_float)


if __name__ == '__main__':
    unittest.main()
