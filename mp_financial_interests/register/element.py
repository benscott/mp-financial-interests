import re
import unicodedata

from mp_financial_interests.lib.exceptions import MissingInterestTypeException, MissingParentException
from mp_financial_interests.lib.helpers import normalise_text, remove_remuneration_bands


class RegisterElement:

    # Regex to extract type code - needs to be attached to start of stirng,
    # Otherwise we get a load of junk
    re_type_code = re.compile('^(\d{1,2})\.', re.IGNORECASE)

    # This will prefer updated date, to registered date.
    # (Registered 30 June 2011; updated 4 October 2012) => 4 October 2012
    # (Registered 26 October 2012) => 26 October 2012
    re_registered_date = re.compile(r'.*?(?:Updated).{0,3}?([0-9]{1,2} [a-z]+ [0-9]{4})|(?:Registered).{0,3}?([0-9]{1,2} [a-z]+\s?[0-9]{4})',
                                    flags=re.IGNORECASE | re.MULTILINE | re.DOTALL
                                    )

    def __init__(self, element):
        self._element = element

    @property
    def name(self):
        # Beautifulsoup element name
        return self._element.name

    @property
    def text(self):
        return self._get_normalized_text()

    @property
    def registration_date(self):
        return self._parse_registration_date()

    @property
    def interest_type_code(self):
        return self._parse_interest_type_code()

    @property
    def html_classes(self):
        return self._element.get('class') or []

    @property
    def indentation_class(self):
        html_classes = [c for c in self.html_classes if 'indent' in c]
        try:
            return html_classes[0]
        except IndexError:
            return None

    def has_html_classes(self, html_classes):
        return bool(set(self.html_classes).intersection(set(html_classes)))

    def has_registration_date_or_amount(self):
        return self.text_contains('£') or bool(self.registration_date)

    def text_contains(self, text):
        return text.lower() in remove_remuneration_bands(self.text).lower()

    def contains_tag(self, tag_name):
        return self._element.find(tag_name)

    def text_equals(self, text):
        return text == self.text

    def _get_normalized_text(self):
        return normalise_text(self._element.getText("\n").strip())

    def _parse_registration_date(self):
        m = self.re_registered_date.search(self.text)
        try:
            # Prefer updated to registered date
            return m.group(1) or m.group(2)
        except AttributeError:
            return None

    def _parse_interest_type_code(self):
        try:
            return int(self.re_type_code.search(self.text).group(1))
        except AttributeError:
            return None

    def __repr__(self):
        return '<RegisterElement {}>'.format(self._element.name)
