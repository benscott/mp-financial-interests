
from __future__ import absolute_import
import re
import pandas as pd
from pandas import HDFStore
import numpy as np
import logging
import name_tools
import warnings


from mp_financial_interests.register.index import RegisterIndexPage
from mp_financial_interests.lib.helpers import normalise_member_name, decimalize


logger = logging.getLogger()

warnings.filterwarnings('ignore', category=pd.io.pytables.PerformanceWarning)

pd.options.display.float_format = '£{:,.2f}'.format


class Interests:

    columns = [
        'member_name',
        'title',
        'type_code',
        'amount',
        'date',
        'description',
        'session',
    ]

    def __init__(self, session=None, member_name=None, clear_cache=False):
        self.session = session
        self.member_name = member_name
        self._group_by = set()
        self._filter = None
        self._order_by = None
        self.cache = HDFStore('/tmp/mp_cache.h5')
        cache_key = self._replace_invalid_charcaters('_'.join(filter(None, [
            'mp',
            session,
            self.member_name
        ]
        )))
        if clear_cache:
            self.clear_cache(cache_key)

        try:
            self._dataframe = self.cache[cache_key]
        except KeyError:
            self._dataframe = pd.DataFrame(
                columns=self.columns
            )
            self._parse_registers()
            self.cache[cache_key] = self._dataframe

    @staticmethod
    def _replace_invalid_charcaters(member_name):
        try:
            return member_name.replace(' ', '_').replace(',', '').replace('-', '_').lower()
        except AttributeError:
            return None

    def _parse_registers(self):
        index = RegisterIndexPage()
        for session_register in index:
            # If user has specified annual session, skip any non-matching sessions
            if self.session and self.session != session_register.session:
                continue

            for member_page in session_register.members_page:
                if self.member_name and normalise_member_name(self.member_name) != member_page.member_name:
                    continue

                logger.info("Processing member %s - %s (%s).",
                            member_page.member_name, session_register.session, member_page.url)
                for interest in member_page.get_interests():
                    self.add_interest(member_page.member_name, interest)

    def add_interest(self, member_name, interest):
        row = [member_name]
        row += [getattr(interest, c)
                for c in self.columns if c != 'member_name']
        self._dataframe.loc[len(self._dataframe)] = row

    @property
    def total(self):
        self._group_by = []
        return decimalize(self.data['amount'].sum())

    @property
    def member_total(self):
        self.set_group_by(['member_name'])
        return self.data

    @property
    def member_total_per_session(self):
        self.set_group_by(['member_name', 'session'])
        return self.data

    @property
    def data(self):
        df = self._dataframe
        if self._filter:
            df = df[self._dataframe['description'].str.contains(
                self._filter, flags=re.IGNORECASE)]
        if self._group_by:
            df = df.groupby(tuple(self._group_by))[
                'amount'].sum().reset_index()
        if self._order_by:
            df = df.sort_values(self._order_by, ascending=False)
        return df

    def group_by_member(self):
        self._group_by.add('member_name')

    def group_by_session(self):
        self._group_by.add('session')

    def set_group_by(self, group_by):
        self._group_by = group_by

    def set_order_by(self, order_by):
        self._order_by = order_by

    def filter_by_type(self, type_code):
        return self.data[self.data['type_code'] == type_code]

    def total_by_type(self, type_code):
        return decimalize(self.filter_by_type(type_code)['amount'].sum())

    def set_filter(self, term):
        self._filter = term

    def to_table(self):
        return self.data.to_string(header=True)

    def to_csv(self, file_name):
        self._dataframe['amount'] = self._dataframe['amount'].astype(float)
        self.data.to_csv(file_name, encoding='utf-8', float_format='£%.2f')
        logger.info("Saved CSV %s", file_name)

    def clear_cache(self, cache_key):
        try:
            self.cache.remove(cache_key)
        except KeyError:
            pass
