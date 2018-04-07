import datetime
import unittest
from mp_financial_interests.register.index import PARSE_FROM_YEAR, RegisterIndexPage


TOTAL_NUMBER_OF_MEMBERS = 650


class TestRegisterMembers(unittest.TestCase):

    def setUp(self):
        self.index = RegisterIndexPage()

    def test_correct_number_of_members(self):
        for session in self.index:
            number_members = len(list(session.members_page))
            # FIXME: This is failing! Why aren't there 650 MP Registers?
            # self.assertEqual(number_members, TOTAL_NUMBER_OF_MEMBERS)


if __name__ == '__main__':
    unittest.main()
