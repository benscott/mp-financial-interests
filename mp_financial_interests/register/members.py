
import os
import re

from mp_financial_interests.register.page import RegisterPage
from mp_financial_interests.register.member import RegisterMemberPage
from mp_financial_interests.lib.helpers import normalise_member_name


class RegisterMembersPage(RegisterPage):

    def __init__(self, url, session):
        self.url = url
        self.session = session
        self._members = self._get_members()

    def __getitem__(self, period):
        return self._sessions[period]

    def __len__(self):
        return len(self._members)

    def __iter__(self):
        return iter(self._members.values())

    def keys(self):
        return self._members.keys()

    def _get_members(self):
        members = {}
        content = self._soup.find('div', {"id": "mainTextBlock"})
        ignore_hrefs = ['part1contents.htm', 'part2contents.htm']
        for a in content.findAll('a'):
            href = a.get('href')
            # Only include if there is an actual href to a webpage (.htm)
            if href and '.htm' in href and href not in ignore_hrefs:
                member_name = normalise_member_name(a.text)
                members[member_name] = RegisterMemberPage(
                    member_name, self.session, self.get_relative_url(href)
                )
        return members

    def __repr__(self):
        return '<RegisterMembersPage {}>'.format(self.url)
