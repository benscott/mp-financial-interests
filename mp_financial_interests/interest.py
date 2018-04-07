import re
import abc
import logging


from mp_financial_interests.lib.formatters import currency_to_float
from mp_financial_interests.interest_types import interest_types
from mp_financial_interests.lib.helpers import normalise_text, remove_remuneration_bands, decimalize


logger = logging.getLogger()


class Interest:

    # Regex for extracting money value from a string - eg: £1,000
    re_amount = re.compile(
        r".*?(?:£)(?:\s+)?([0-9,\.\-]+)", flags=re.MULTILINE | re.DOTALL)

    def __init__(self, session, type_code=None):
        self.session = session
        self.date = None
        self.lines = []
        self._type = None
        self._parent = None
        self._amount = None
        if type_code:
            self.set_type(type_code)

    def __bool__(self):
        return bool(len(self.lines) and self._type)

    @property
    def title(self):
        return self._type.title

    @property
    def type_code(self):
        return self._type.type_code

    def add_line(self, line):
        self.lines.append(line)

    def set_parent(self, parent):
        self._parent = normalise_text(parent)

    def get_parent(self):
        return self._parent

    def set_date(self, date):
        self.date = date

    def set_amount(self, amount):
        self._amount = amount

    def _get_interest_type(self, type_code):
        for interest_type in interest_types:
            if interest_type.type_code == type_code and interest_type.is_code_of_conduct_for(self.session):
                return interest_type
        raise Exception('No interest type for code %s - %s',
                        type_code, self.session)

    def set_type(self, type_code):
        self._type = self._get_interest_type(type_code)

    @property
    def line_text(self):
        return [l.text for l in self.lines]

    @property
    def flattened_lines(self):
        return ' '.join(self.line_text)

    @property
    def description(self):
        if self._parent and self._parent not in self.flattened_lines:
            return self._parent + self.flattened_lines
        return self.flattened_lines

    @property
    def amount(self):
        # Entries can be x times £, total £
        # So we always want to select the last entry
        if not self._amount:
            self.parse_amount()
        return self._amount

    def parse_amount(self):
        self._amount = self._parse_maximum_amount_from_lines()

    def _extract_amount_from_lines(self):
        # Some interests include the renumeration band the interest falls into e.g. (£45,001-£50,000)
        # So try extracting the amount without the bounds, and if that doesn't work, with the bands
        for lines in [remove_remuneration_bands(self.flattened_lines), self.flattened_lines]:
            amount = self.re_amount.findall(lines)
            if amount:
                return amount

    def _parse_maximum_amount_from_lines(self):
        amount = self._extract_amount_from_lines()
        if not amount:
            return None
        try:
            # Always get the highest value - hopefully this will be the total
            return max(list(map(currency_to_float, amount)))
        except ValueError:
            pass
        return None

    def amount_is_required(self):
        if self._type.amount_required:
            if self.is_unremunerated() or self.is_not_trading() or self.is_donated_to_charity():
                return False
            return True
        return False

    def is_donated_to_charity(self):
        return self.is_in_lines('donated to charity')

    def is_rectification(self):
        return self.one_of_is_in_lines([
            'rectification procedure',
            'Correction to earlier register',
        ])

    def is_in_lines(self, match):
        return match.lower() in self.description.lower()

    def one_of_is_in_lines(self, matches):
        for match in matches:
            if self.is_in_lines(match):
                return True
        return False

    def is_unremunerated(self):
        # Added farmer as exact income is never recorded
        return self.one_of_is_in_lines([
            'not for profit',
            'unremunerated',
            'no remuneration',
            'no payment received',
            'I make no drawings',
            'not receiving any money',
            'farmer',
            'crofter',
            'unpaid',
            'territorial army',
            'voluntary service',
            'No fixed remuneration',
            'not paid as the activity is loss-making',
            'non-practising',
            'no further payments',
            'no personal payments',
            'Royal Navy Reserve',
            'Reserve Officer',
            'Payment made direct to local charity',
            'Fee waived',
            'Fees waived'
        ])

    def is_not_trading(self):
        return self.is_in_lines('not trading')

    def __repr__(self):
        return '<Interest {}>'.format(self.amount)
