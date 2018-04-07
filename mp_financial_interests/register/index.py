import re

from collections import OrderedDict


from mp_financial_interests.register.page import RegisterPage
from mp_financial_interests.register.session import RegisterSessionPage


# Interests pre-2010 are in a completely different format
PARSE_FROM_YEAR = 2010


class RegisterIndexPage(RegisterPage):

    """
    Index of registers - parses the list of annual registers, available at:
    http://www.parliament.uk/mps-lords-and-offices/standards-and-financial-interests/parliamentary-commissioner-for-standards/registers-of-interests/register-of-members-financial-interests/
    """

    url = 'http://www.parliament.uk/mps-lords-and-offices/standards-and-financial-interests/parliamentary-commissioner-for-standards/registers-of-interests/register-of-members-financial-interests/'

    # Regex for parsing years covered from title
    # For example, matches 2010-11
    re_annual_period = re.compile('.*((\d{4})-(\d{2}))')

    def __init__(self):
        self._sessions = self._get_annual_sessions()

    def __getitem__(self, period):
        return self._sessions[period]

    def __len__(self):
        return len(self._sessions)

    def __iter__(self):
        return iter(self._sessions.values())

    def keys(self):
        return self._sessions.keys()

    @property
    def sessions(self):
        return self._sessions

    def _get_annual_sessions(self):
        sessions = OrderedDict()
        for link in self._parse_index_page_links():
            annual_period = self._extract_annual_period(link.text)
            if self._annual_period_after_parse_from_year(annual_period):
                sessions[annual_period['range']] = RegisterSessionPage(
                    annual_period['range'], link['href']
                )
        return sessions

    @staticmethod
    def _annual_period_after_parse_from_year(annual_period):
        return annual_period and annual_period['year_from'] >= PARSE_FROM_YEAR

    def _parse_index_page_links(self):
        # Yield all the link contained in <li> elements
        # From the main page body div#content-small
        inner_content = self._soup.find('div', {"id": "content-small"})
        for li in inner_content.findAll('li'):
            yield li.find('a', href=True)

    def _extract_annual_period(self, link_text):
        # Extract annual period (YYYY-YY) from the link text
        m = self.re_annual_period.match(link_text)
        try:
            return {
                'range': m.group(1),
                'year_from': int(m.group(2)),
                'year_to': int(m.group(3))
            }
        except AttributeError:
            return None
