import datetime
import unittest
from bs4 import BeautifulSoup

from mp_financial_interests.interests import Interests
from mp_financial_interests.interest import Interest
from mp_financial_interests.register.line import RegisterLine
from mp_financial_interests.lib.helpers import decimalize


class TestInterests(unittest.TestCase):

    NUMBER_OF_MEMBERS = 2
    NUMBER_OF_INTEREST_TYPES = 3
    SESSIONS = ['2015-16', '2016-18']
    AMOUNT = 10000

    def setUp(self):
        self.interests = Interests(session='1000-11')

        line_element = BeautifulSoup(
            '<p>£10,000 for something or other</p>', "html5lib")

        line = RegisterLine(line_element)

        for session in self.SESSIONS:
            for member_number in range(0, self.NUMBER_OF_MEMBERS):
                for interest_type in range(0, self.NUMBER_OF_INTEREST_TYPES):
                    interest = Interest(session)
                    interest.set_type(interest_type + 1)
                    interest.add_line(line)
                    member_name = 'Test User {}'.format(member_number)
                    self.interests.add_interest(
                        interest=interest, member_name=member_name)

    def test_interests_total(self):
        total_amount = self.AMOUNT * self.NUMBER_OF_INTEREST_TYPES * \
            self.NUMBER_OF_MEMBERS * len(self.SESSIONS)
        self.assertEqual(self.interests.total, total_amount)

    def test_interests_total_for_members(self):
        total_amount_per_member = self.AMOUNT * \
            self.NUMBER_OF_INTEREST_TYPES * len(self.SESSIONS)
        member_total = self.interests.member_total
        for amount in member_total['amount']:
            self.assertEqual(amount, total_amount_per_member)

    def test_interests_total_for_interest_type(self):
        total_amount_per_type = self.AMOUNT * \
            self.NUMBER_OF_MEMBERS * len(self.SESSIONS)
        for interest_type in range(0, self.NUMBER_OF_INTEREST_TYPES):
            total_by_type = self.interests.total_by_type(interest_type + 1)
            self.assertEqual(total_by_type, total_amount_per_type)

    def test_interests_total_for_sessions(self):
        total_amount_per_session = self.AMOUNT * self.NUMBER_OF_INTEREST_TYPES * \
            self.NUMBER_OF_MEMBERS
        self.interests.group_by_session()
        for amount in self.interests.data['amount']:
            self.assertEqual(amount, total_amount_per_session)

    def test_interests_register_parsing(self):
        interests = Interests(session='2013-14', member_name='ADAMS, Nigel')
        self.assertEqual(interests.total, decimalize(20685.37))


if __name__ == '__main__':
    unittest.main()
