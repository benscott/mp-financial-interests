import os
import re

from urllib.parse import urlparse
from urllib.parse import urljoin

from mp_financial_interests.register.page import RegisterPage
from mp_financial_interests.register.members import RegisterMembersPage
from mp_financial_interests.lib.exceptions import MissingMembersPageException


class RegisterSessionPage(RegisterPage):

    """

    Registers are additive
    How does this one link to the annual members page
    Possibly loop through to find all 

    """

    re_members_session = re.compile("Session (\d{4}\-\d{2})")

    def __init__(self, session, url):
        self.session = session
        self.url = url

    @property
    def members_page(self):
        return self._get_members_page()

    @staticmethod
    def _is_members_page_link(url):
        # Members page file names are either contents.htm post 14-15
        # Or part1contents.htm before
        member_file_names = ['part1contents.htm', 'contents.htm']
        return os.path.basename(url) in member_file_names

    def _get_members_page(self):
        for members_page_url in self._get_members_page_url():
            # Registry has lots of links to members pages for different sessions
            # So ensure the members page is for the correct session before returning it
            if self._is_members_page_for_correct_session(members_page_url):
                return RegisterMembersPage(members_page_url, self.session)

        # If we've reached here, no page was found - raise an exception
        raise MissingMembersPageException(self.period, self.url)

    def _is_members_page_for_correct_session(self, members_page_url):
        members_page_session = self._get_members_page_session(members_page_url)
        return self.session == members_page_session

    def _get_members_page_session(self, members_page_url):
        soup = self._get_soup(members_page_url)
        title_block = soup.find('div', {"id": "titleBlockLinks"})
        return self._extract_session_from_element(title_block)

    def _get_page_session(self):
        title_block = self._soup.find('div', {"id": "titleBlockLinks"})
        if not title_block:
            title_block = self._soup.find(
                'div', {"id": "maincontent"}).find('table')

        return self._extract_session_from_element(title_block)

    def _extract_session_from_element(self, element):
        try:
            session_text = element.find(text=self.re_members_session)
        except AttributeError:
            raise
        else:
            return self.re_members_session.match(session_text).group(1)

    def _get_members_page_url(self):
        content = self._soup.find('div', {"id": "maincontent"})
        for a in content.findAll('a'):
            if self._is_members_page_link(a['href']):
                yield self.get_relative_url(a['href'])

    def __repr__(self):
        return '<RegisterAnnualPage {}>'.format(self.session)
