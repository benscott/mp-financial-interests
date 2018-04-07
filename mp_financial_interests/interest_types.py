
from mp_financial_interests.interest_type import InterestType2010, InterestType2015

# List of interest types we're interested in
# See http://www.publications.parliament.uk/pa/cm/cmregmem/1017/introduction.htm

interest_types = [
    # 2015 Types
    InterestType2015(1, 'Employment and earnings', True),
    InterestType2015(2, 'Donations and other support (including loans)', True),
    InterestType2015(
        3, 'Gifts, benefits and hospitality from UK sources'),
    InterestType2015(4, 'Visits outside the UK'),
    InterestType2015(
        5, 'Gifts and benefits from sources outside the UK'),
    InterestType2015(6, 'Land and property'),
    InterestType2015(7, 'Shareholdings'),
    InterestType2015(8, 'Miscellaneous'),
    InterestType2015(9, 'Family members employed'),
    InterestType2015(10, 'Family members engaged in lobbying'),
    # 2010 Types
    InterestType2010(1, 'Directorships'),
    InterestType2010(2, 'Employment and earnings', True),
    InterestType2010(3, 'Clients', True),
    InterestType2010(4, 'Sponsorship or financial or material support', True),
    InterestType2010(5, 'Gifts, benefits and hospitality'),
    InterestType2010(6, 'Overseas visits'),
    InterestType2010(7, 'Overseas benefits and gifts'),
    InterestType2010(8, 'Land and property'),
    InterestType2010(9, 'Registrable shareholdings'),
    InterestType2010(10, 'Loans and other controlled transactions'),
    InterestType2010(11, 'Miscellaneous'),
]
