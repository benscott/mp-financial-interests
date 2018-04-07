import abc
import logging
from mp_financial_interests.lib.helpers import normalise_member_name
from mp_financial_interests.interest_types import interest_types


logger = logging.getLogger()


INTEREST_TYPE_ERROR_CODE = 1
PARENT_LINE_ERROR_CODE = 2
AMOUNT_ERROR_CODE = 3


class Erratum:

    __metaclass__ = abc.ABCMeta

    def __init__(self, commit_interest=True, **kwargs):
        self.commit_interest = commit_interest
        # kwargs provides additonal terms to filter on
        # i.e. if session and type code are provided, the error will
        # only match the correct session and type code. This allows us to create
        # errors that match an MPs entire session:
        #      Erratum(member_name='XXX', session='YYYY-YY')
        # or an entire type of interests for a session:
        #      Erratum(member_name='XXX', session='YYYY-YY', type_code=X)
        if kwargs.get('member_name', None):
            kwargs['member_name'] = normalise_member_name(
                kwargs.get('member_name'))
        self.filter_on = set(tuple(kwargs.items()))

    @abc.abstractproperty
    def error_code(self):
        return None

    @abc.abstractproperty
    def error_message(self):
        return None


class InterestTypeErratum(Erratum):

    error_code = INTEREST_TYPE_ERROR_CODE
    error_message = 'Could not extract interest type code'

    def process_error(self, interest, line):
        interest.add_line(line)


class ParentLineErratum(Erratum):

    error_code = PARENT_LINE_ERROR_CODE
    error_message = 'Missing parent line'

    # Extends Erratum but adds a flag denoting whether the interest should be committed
    def __init__(self, commit_interest=False, replacement_line=None, **kwargs):
        super().__init__(commit_interest, **kwargs)
        self.replacement_line = replacement_line

    def process_error(self, interest, line):
        # We only commit if the replacement amount has been changed
        if self.replacement_line and self.replacement_line not in interest.flattened_lines:
            interest.set_parent(self.replacement_line)


class AmountErratum(Erratum):

    error_code = AMOUNT_ERROR_CODE
    error_message = 'Amount missing'

    # Extends Erratum but adds a flag denoting whether the interest should be committed
    def __init__(self, commit_interest=True, replacement_amount=None, **kwargs):
        super().__init__(commit_interest, **kwargs)
        self.replacement_amount = replacement_amount

    def process_error(self, interest, line):
        # We only commit if the replacement amount has been changed
        if self.replacement_amount:
            interest.set_amount(self.replacement_amount)
