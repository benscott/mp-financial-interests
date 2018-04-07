import os
import re
from urllib.parse import urlparse, urlunparse
from itertools import chain
import unicodedata
from decimal import Decimal


from mp_financial_interests.lib.exceptions import MemberNameParseException


re_member_name = re.compile(
    r'(?P<surname>[a-z\-]+),.*?\b(?P<forename>[a-zéâè]+)$', re.IGNORECASE | re.UNICODE)

re_double_spaces = re.compile(r'\s\s+')

re_remuneration_bands = re.compile(
    r'£0-5,+000|up to £5,?000|£\d+,+00[01]-£\d+,+000', flags=re.MULTILINE | re.DOTALL | re.IGNORECASE)

win1252_character_mappings = str.maketrans(
    """‚ƒ„†ˆ‹‘’“”•–—›""",
    """'f"*^<''""--->"""
)


def normalise_member_name(name):
    # Remove any trailing spaces so the end of line match works correctly
    # Some MP names include honorifics in the middle:
    # ABBOTT, Diane is also ABBOTT, Ms Diane
    # So to create a nomalised name, we take the first and last parts
    name = re.sub(r'[A-Z]\.', '', name)
    name = name.strip()
    m = re_member_name.search(name)
    try:
        return '{}, {}'.format(m.group('surname'), m.group('forename')).lower()
    except AttributeError:
        raise MemberNameParseException(name)


def remove_remuneration_bands(text):
    return re_remuneration_bands.sub('', text)


def replace_win1252_characters(text):
    """Replace Win1252 symbols with ASCII chars or sequences"""
    return text.translate(win1252_character_mappings)


def normalise_text(text):
    text = replace_win1252_characters(text)
    # Remove zero width space character
    text = text.replace('\u200b', '')
    text = replace_new_lines(text)
    text = unicodedata.normalize('NFKC', text)
    return remove_double_spaces(text)


def remove_double_spaces(text):
    return re_double_spaces.sub(" ", text)


def replace_new_lines(text):
    return text.replace('\n', ' ')


def decimalize(i):
    try:
        return Decimal(i).quantize(Decimal('.01'))
    except TypeError:
        return None
