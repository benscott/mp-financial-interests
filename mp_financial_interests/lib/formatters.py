import re
from decimal import Decimal


def currency_to_float(currency):
    """
    Convert currency string to int
    @param str: currency to convert
    @return: int
    """

    currency = currency.strip()

    # If that last char is a full stop, remove it
    currency = currency.rstrip('.')

    # If the last char is a - remove it
    currency = currency.rstrip('-')

    # Common problem is adding extra decimal points, instead of thousands comma separator
    # SO if we have more than one decimal point, remove it
    if currency.count('.') > 1:
        currency = currency.replace('.', '', currency.count('.') - 1)

    # Some currency values have a range: e.g.: Spencer, Mark 20-14-15: £5-10,000
    # We want to make sure these aren't recorded as £5, so - is included in the regex
    # But we want to split on it and take the upper bounds
    if '-' in currency:
        currency = currency.split('-')[1]

    value = re.sub(r'[^\d.]', '', currency.replace(',', '').rstrip('.'))

    try:
        value = Decimal(value)
    except AttributeError:
        print('Could not parse amount: %s' % currency)
        raise

    return float(value)
