import abc
import datetime
from collections import namedtuple
import unittest
import warnings

from mp_financial_interests.register.member import RegisterMemberPage
from mp_financial_interests.interests import Interests
from mp_financial_interests.interest_types import interest_types
from mp_financial_interests.lib.helpers import decimalize, normalise_member_name


InterestAmount = namedtuple('InterestAmount', ['type', 'total'])


class BaseTestRegisterMember:

    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def session(self):
        return None

    @abc.abstractproperty
    def url(self):
        return None

    @abc.abstractproperty
    def member_name(self):
        return None

    @abc.abstractproperty
    def interest_amounts(self):
        return {}

    def setUp(self):

        warnings.filterwarnings('ignore', category=ImportWarning)

        normalized_memeber_name = normalise_member_name(self.member_name)

        self.member_page = RegisterMemberPage(
            url=self.url,
            session=self.session,
            member_name=normalized_memeber_name
        )

        self.interests = Interests(
            member_name=normalized_memeber_name,
            session=self.session
        )

    def test_interests_dataframe_matches_parsed_interests_total(self):
        interests = self.member_page.get_interests()
        interests_total = decimalize(
            sum(i.amount for i in interests if i.amount)
        )
        self.assertEqual(self.interests.total, interests_total)

    def test_amounts_match_parsed_interests(self):
        for type_code, amount_total in self.interest_amounts:
            interests_type_total = self.interests.total_by_type(type_code)
            amount_total = decimalize(
                amount_total) if amount_total else amount_total
            self.assertEqual(amount_total, interests_type_total)

    def test_amounts_total_matches_parsed_total(self):
        amounts_total = decimalize(sum(i.total for i in self.interest_amounts))
        self.assertEqual(self.interests.total, amounts_total)


class TestRichardOttoway2010Interests(BaseTestRegisterMember, unittest.TestCase):

    url = 'https://publications.parliament.uk/pa/cm/cmregmem/120430/ottaway_richard.htm'
    member_name = 'OTTAWAY, Richard'
    session = '2010-12'
    interest_amounts = [
        InterestAmount(2, 150),
        InterestAmount(5, 1150),
        InterestAmount(6, 1600),
        InterestAmount(8, 0)
    ]


class TestGuyOpperman2010Interests(BaseTestRegisterMember, unittest.TestCase):

    url = 'http://www.publications.parliament.uk/pa/cm/cmregmem/120430/opperman_guy.htm'
    member_name = 'Opperman, Guy'
    session = '2010-12'
    interest_amounts = [
        InterestAmount(2, 104295.95),
        InterestAmount(4, 13000),
    ]


class TestJacobReesMogg2010Interests(BaseTestRegisterMember, unittest.TestCase):

    url = 'http://www.publications.parliament.uk/pa/cm/cmregmem/120430/rees-mogg_jacob.htm'
    member_name = 'rees-mogg, jacob'
    session = '2010-12'
    interest_amounts = [
        InterestAmount(1, 99227.89),
        InterestAmount(2, 600),
        InterestAmount(3, 0),
        InterestAmount(8, 0),
        InterestAmount(9, 0),
    ]


class TestSimonReevell2014Interests(BaseTestRegisterMember, unittest.TestCase):

    url = 'http://www.publications.parliament.uk/pa/cm/cmregmem/150330/reevell_simon.htm'
    member_name = 'REEVELL, Simon'
    session = '2014-15'
    interest_amounts = [
        InterestAmount(2, 52739.73),
        InterestAmount(4, 2000),
    ]


class TestDianeAbbott2016Interests(BaseTestRegisterMember, unittest.TestCase):

    url = 'https://publications.parliament.uk/pa/cm/cmregmem/170502/abbott_diane.htm'
    member_name = 'Abbott, Diane'
    session = '2016-17'
    interest_amounts = [
        InterestAmount(1, 955),
        InterestAmount(4, 8361.80),
        InterestAmount(8, 0),
    ]


class TestCrispinBlunt2017Interests(BaseTestRegisterMember, unittest.TestCase):

    url = 'https://publications.parliament.uk/pa/cm/cmregmem/180305/blunt_crispin.htm'
    member_name = 'Blunt, Crispin'
    session = '2017-19'
    interest_amounts = [
        InterestAmount(1, 1066.67),
        InterestAmount(2, 60000),
        InterestAmount(4, 8329),
    ]


if __name__ == '__main__':
    unittest.main()


if __name__ == '__main__':
    unittest.main()
