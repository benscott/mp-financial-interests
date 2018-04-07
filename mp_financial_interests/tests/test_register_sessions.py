import datetime
import unittest
from mp_financial_interests.register.index import PARSE_FROM_YEAR, RegisterIndexPage


class TestRegisterSessions(unittest.TestCase):

    def setUp(self):
        self.index = RegisterIndexPage()

    def test_sessions_are_for_correct_year(self):
        for session_register in self.index:
            parsed_session = session_register._get_page_session()
            self.assertEqual(parsed_session, session_register.session)


if __name__ == '__main__':
    unittest.main()
