import datetime
import unittest
from mp_financial_interests.register.index import PARSE_FROM_YEAR, RegisterIndexPage


MULTI_YEAR_SESSIONS = [2010, 2017]


class TestRegisterIndex(unittest.TestCase):

    def setUp(self):
        self.index = RegisterIndexPage()

    def _get_annual_sessions(self):
        current_year = datetime.datetime.today().year + 1
        sessions = set()
        for y in range(PARSE_FROM_YEAR, current_year):
            if y - 1 in MULTI_YEAR_SESSIONS:
                continue
            year_to = y + 1 if y not in MULTI_YEAR_SESSIONS else y + 2
            sessions.add('{year_from}-{year_to}'.format(
                year_from=y,
                year_to=str(year_to)[-2:]
            ))
        return sessions

    def test_annual_sessions_have_been_parsed(self):
        # Some sessions are for two years - 2010-2012 & 2017-2019
        expected_sessions = self._get_annual_sessions()
        index_sessions = set(self.index.keys())
        self.assertEqual(index_sessions, expected_sessions)


if __name__ == '__main__':
    unittest.main()
