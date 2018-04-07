import re
import unicodedata

from mp_financial_interests.lib.exceptions import MissingInterestTypeException, MissingParentException
from mp_financial_interests.lib.helpers import normalise_text, remove_remuneration_bands
from mp_financial_interests.register.element import RegisterElement


class RegisterLine:

    TERTIARY_INDENT_CLASSES = ['indent']
    SUB_ENTRY_INDENT_CLASSES = ['indent2', 'indent3']

    re_indent_level = re.compile(r'.*?([0-9]+)$')

    def __init__(self, line):
        self.line = line
        self._element = RegisterElement(line)
        self._max_indent_level = max(
            (self._extract_indent_level(i)
             for i in self.SUB_ENTRY_INDENT_CLASSES)
        )

    @property
    def text(self):
        return self._element.text

    @property
    def indent_html_class(self):
        return self._element.indentation_class

    @property
    def indent_class_level(self):
        # The number extracted from the indent class indent1=>1, indent=>None
        if self.indent_html_class:
            return self._extract_indent_class_level(self.indent_html_class)

    @staticmethod
    def _extract_indent_class_level(class_):
        m = re.match(r'.*?([0-9]+)$', class_)
        try:
            return int(m.group(1))
        except AttributeError:
            if 'indent' in class_:
                return 0

    def is_page_header(self, member_name):
        h_tags = ['h2', 'h3']
        previous_element = self._get_previous_element(element_name=h_tags)
        if self._element.name in h_tags or (self._element.contains_tag('strong') and previous_element):
            # Is this line a page header - e.g. ABBOTT, Diane (Hackney North and Stoke Newington)
            member_surname, member_forename = member_name.split(',')
            # print(member_forename)
            pattern = '.?({member_surname}.+{member_forename}.+\(:?.+\))'.format(
                member_surname=member_surname.strip(),
                member_forename=member_forename.strip()
            )
            return bool(re.search(pattern, self._element.text, re.IGNORECASE))
        return False

    def is_title(self):
        # If the title contains 'rectification procedure' it's not a title
        if self.is_rectifcation():
            return False

        # Header can either be in a paragraph <p><h3></h3><p> Or just a header tag
        if self.line.find('h3') or self._element.name == 'h3':
            return True

        # Some entries are in strong tags, for example:
        # https://publications.parliament.uk/pa/cm/cmregmem/170502/whittingdale_john.htm
        # So if the line is indented, it's not a title tag
        if self.is_indented():
            return False

        # We need to find all <strong> and loop through - some titles have multiple with empty ones:
        # https://publications.parliament.uk/pa/cm/cmregmem/140512/swayne_desmond.htm
        for el in self.line.find_all('strong'):
            strong_el = RegisterElement(el)
            # If we have a strong element, make sure it's not empty before assuming it's a title
            if strong_el.text:
                return True

        return False

    def is_indented(self):
        return self._element.has_html_classes(self.TERTIARY_INDENT_CLASSES + self.SUB_ENTRY_INDENT_CLASSES)

    def is_rectifcation(self):
        return self._element.text_contains('rectification procedure')

    def is_previous_line_header(self):
        previous_element = self._get_previous_element()
        return previous_element and previous_element.name == 'h3' and previous_element.interest_type_code

    def _get_previous_element(self, **kwargs):
        previous_elements = self._get_previous_elements(**kwargs)
        try:
            return next(previous_elements)
        except StopIteration:
            return None

    def is_nil(self):
        return self._element.text_equals('Nil.') or self._element.text_equals('Nil')

    def is_self_employed_farmer(self):
        # Special case for https://publications.parliament.uk/pa/cm/cmregmem/120430/davies_glyn.htm
        self._element.text_equals('Self-employed farmer.')

    def is_single_character(self):
        # Fixes: http://www.publications.parliament.uk/pa/cm/cmregmem/130422/hunt_jeremy.htm
        return len(self._element.text) <= 1

    def is_empty(self):
        return not self._element.text

    def is_sub_entry(self):
        # Some records are sub-entries, recurring items related to a top-level
        # entry - e.g. https://publications.parliament.uk/pa/cm/cmregmem/130507/abbott_diane.htm
        # They are denoted by increased indentation - classes indent2 & indent3
        return self._element.has_html_classes(self.SUB_ENTRY_INDENT_CLASSES)

    def is_parent_with_sub_entries(self):

        parent_element = self._get_sub_entry_parent_element()
        # If this element has a parent of it's own, it's not a parent
        if parent_element:
            # print('HAS PARENT')
            # print(parent_element.text)
            return False

        # Has a direct sibling with indent2 / indent 3
        if self._element.has_html_classes(self.TERTIARY_INDENT_CLASSES):
            next_el = self._get_next_element()
            # If the next el is a h3, then this isn't a parent with subentries
            # Handles the edge case where a line proceeds a <h3> tag, but the
            # the next section para are incorrectly indented - e.g.
            # https://publications.parliament.uk/pa/cm/cmregmem/150330/dorrell_stephen.htm
            if next_el.name == 'h3':
                return False
            elif next_el.has_html_classes(self.SUB_ENTRY_INDENT_CLASSES):
                return True
        return False

    def is_last_line(self):
        # Is this the last line: has class prevNext (bottom links)
        return self._element.has_html_classes(['prevNext'])

    def has_amount(self):
        return self._element.text_contains('£')

    def has_registration_date_or_amount(self):
        return self.has_amount() or bool(self.registration_date)

    def get_registration_date(self):
        return self._element.registration_date

    def get_sub_entry_parent(self):
        parent_element = self._get_sub_entry_parent_element()
        if not parent_element:
            raise MissingParentException(self.text)
        return parent_element.text

    def get_interest_type_code(self):
        if self._element.interest_type_code:
            return self._element.interest_type_code
        raise MissingInterestTypeException()

    def _find_previous_siblings_with_less_indentation(self):
        # Find previous paragraph that has a different level of indentation
        indent_class_level = self.indent_class_level or 0
        classes = ['indent{}'.format(i if i > 0 else '')
                   for i in range(indent_class_level, self._max_indent_level)
                   ]

        # Find class that has an indent class, that is different to the current line
        # Also excludes the occasional p.spacer lines
        return self._get_previous_elements(class_=lambda c: c not in classes)

    def _get_next_element(self, element_name=['p', 'h3'], class_=lambda c: c != 'spacer'):
        next_el = self.line.findNext(element_name, class_)
        if next_el:
            return RegisterElement(next_el)

    def _get_previous_elements(self, element_name=['p', 'h3'], class_=lambda c: c != 'spacer'):
        for el in self.line.find_previous_siblings(element_name, class_):
            yield RegisterElement(el)

    def _get_sub_entry_parent_element(self):
        for el in self._find_previous_siblings_with_less_indentation():
            # If we hit a h3 tag, don't try finding a parent further back
            if el.name == 'h3' or el.contains_tag('strong'):
                if el.interest_type_code:
                    break
                else:
                    return el
            elif el.text:
                return el

        current_indent = self.indent_class_level or 0
        for el in self._get_previous_elements():
            if el.name == 'h3':
                break

            if not el.text or not el.indentation_class:
                continue

            # If the previous elements indentation is greater than the current line's
            # Then do not look any further back - they are subentries belonging to
            # another record
            el_indent_level = self._extract_indent_class_level(
                el.indentation_class)

            if el_indent_level > current_indent:
                break

            if not el.has_registration_date_or_amount():
                return el

    def _extract_indent_level(self, class_):
        m = self.re_indent_level.match(class_)
        try:
            return int(m.group(1))
        except AttributeError:
            return None

    def __repr__(self):
        return '<RegisterLine {}>'.format(self.text)
