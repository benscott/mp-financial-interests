import os
import re
import logging

from mp_financial_interests.register.page import RegisterPage
from mp_financial_interests.register.line import RegisterLine
from mp_financial_interests.lib.exceptions import MissingInterestTypeException, MissingParentException
from mp_financial_interests.interest import Interest
from mp_financial_interests.lib.helpers import normalise_text, remove_remuneration_bands

from mp_financial_interests.errata import errata
from mp_financial_interests.erratum import INTEREST_TYPE_ERROR_CODE, PARENT_LINE_ERROR_CODE, AMOUNT_ERROR_CODE


logger = logging.getLogger()


class RegisterMemberPage(RegisterPage):

    """
    Class representing a member register page

    https://publications.parliament.uk/pa/cm/cmregmem/180305/abbott_diane.htm

    """

    def __init__(self, member_name, session, url):
        self.member_name = member_name
        self.url = url
        self.session = session
        self._interests = []
        self._initilise_interest()

    def get_interests(self):
        self._parse_interest_entries()
        return self._interests

    def _initilise_interest(self, interest_type_code=None):
        self._interest = Interest(
            session=self.session,
            type_code=interest_type_code
        )

    def _validate_and_commit_interest(self):
        if self._interest:
            if not self._interest.amount:
                # Interests that have been added as part of rectification often don;t have amount
                # Or are addedums to previous lines - e.g. http://www.publications.parliament.uk/pa/cm/cmregmem/150330/danczuk_simon.htm
                # So we ignore them if they don't have an interest date
                if self._interest.is_rectification() and not self._interest.date:
                    self._reset_interest()
                    return
                if self._interest.amount_is_required() and not self._interest.is_rectification():
                    return self._handle_missing_amount_error(self._interest.lines[0])

            self._commit_interest()

    def _commit_interest(self):

        if len(self._interest.lines) > 1:
            lines_with_pounds = sum(
                1 for l in self._interest.lines if l.has_amount())
            # This has multiple interests across lines, but with only one registration date
            if lines_with_pounds > 1:
                self._split_interest()
                return

        self._interests.append(self._interest)
        # Initialise an interest using them same interest type code
        # as preivous one - the interest type code is read once from the
        # title, so needs to persist between each interest
        self._reset_interest()

    def _reset_interest(self):
        # Initialise an interest using them same interest type code
        # as preivous one - the interest type code is read once from the
        # title, so needs to persist between each interest
        self._initilise_interest(self._interest.type_code)

    def _split_interest(self):
        lines = self._interest.lines
        date = self._interest.date
        parent = self._interest.get_parent()
        self._reset_interest()
        for line in lines:
            self._interest.date = date
            if parent:
                self._interest.set_parent(parent)
            self._interest.lines.append(line)
            if line.has_amount():
                self._interest.parse_amount()
                self._interests.append(self._interest)
                self._reset_interest()

        self._reset_interest()

    def _parse_interest_entries(self):

        for line in self._read_lines():

            if line.is_nil() or line.is_empty() or line.is_single_character() or line.is_page_header(self.member_name):
                continue

            if line.is_title():
                self._validate_and_commit_interest()
                if self._process_title(line):
                    # If this is a succesfully processed title line,
                    # no further processing is required
                    continue

            if line.is_last_line():
                # If this is last line & we still have interest data, then yield it
                self._validate_and_commit_interest()
                break

            # if line.text == "Fees received for co-presenting BBC's 'This Week' TV programme. Address: BBC Broadcasting House, Portland Place, London W1A 1AA. (Registered 04 November 2013)":
            #     print(line.is_parent_with_sub_entries())
            #     print(line)
            # else:
            #     continue

            if line.is_parent_with_sub_entries():
                continue
                # Only add if it's not a parent line - these are added to the child interests

            # Some entries span multiple lines (and paragraphs)
            # So we build a list of lines, to be passed to the interest type class
            self._interest.add_line(line)

            # Every entry concludes with date registered - i.e. (Registered 26 October 2016)
            # So try and find the date - and if it exists, commit the entry
            # registered_date = line.get_registration_date()
            if line.get_registration_date():
                self._process_registration_date(line)
                self._validate_and_commit_interest()

    def _process_title(self, line):
        self._validate_and_commit_interest()
        try:
            interest_type_code = line.get_interest_type_code()
        except MissingInterestTypeException:
            # If the line has a registered date, we can assume it's a normal
            # entry that has just been added as <h3> tags - for example:
            # https://publications.parliament.uk/pa/cm/cmregmem/150330/hendry_charles.htm
            if not line.get_registration_date():
                # Only raise an error if the line drectly before isn't a header
                if not line.is_previous_line_header() or line.is_self_employed_farmer():
                    self._handle_missing_interest_type_error(line)
                    return True

            return False
        else:
            self._interest.set_type(interest_type_code)
            return True

    def _process_registration_date(self, line):
        registered_date = line.get_registration_date()
        self._interest.set_date(registered_date)
        # If this is a subentry item, include the parent line as well
        if line.is_sub_entry():
            try:
                parent = line.get_sub_entry_parent()
            except MissingParentException:
                # If the line is immediately after a h3 header then there's
                # No need to raise an error - we can make the assumption the
                # indentation is just incorrect
                if not line.is_previous_line_header():
                    self._handle_missing_parent_error(line)
            else:
                self._interest.set_parent(parent)

    def _handle_missing_interest_type_error(self, line):
        self._handle_error(INTEREST_TYPE_ERROR_CODE, line)

    def _handle_missing_parent_error(self, line):
        self._handle_error(PARENT_LINE_ERROR_CODE, line)

    def _handle_missing_amount_error(self, line):
        # Some parent entries have a registered date - but no amount
        # So if a line is a parent with subentries, ignore the error
        if not line.is_parent_with_sub_entries():
            self._handle_error(AMOUNT_ERROR_CODE, line)
            self._reset_interest()

    def _handle_error(self, error_code, line):
        params = {
            'interest': self._interest,
            'error_code': error_code,
            'member_name': self.member_name,
            'session': self.session,
            'line': line,
            'type_code': self._interest.type_code if self._interest else None
        }
        erratum = errata.handle_error(**params)
        if erratum:
            if erratum.commit_interest:
                self._commit_interest()

    def _read_lines(self):
        content = self._soup.find('div', {"id": "mainTextBlock"})
        # Start by finding the page h2
        h2 = content.find('h2')
        # Loop through each row
        first_el = h2.find_next_sibling()
        return self._recursive_next_sibling(first_el)

    def _line_has_nested_elements(self, line):
        return line.find(['h3', 'p'])

    def _recursive_next_sibling(self, el):
        # Needs to be recursive so nested elements are also located:
        # https://publications.parliament.uk/pa/cm/cmregmem/120430/ottaway_richard.htm
        while True:
            if not el:
                break
            nested_elements = self._line_has_nested_elements(el)
            if nested_elements:
                yield from self._recursive_next_sibling(nested_elements)
            yield RegisterLine(el)
            el = el.find_next_sibling()

    def __repr__(self):
        return '<RegisterMemberPage {}>'.format(self.member_name)
