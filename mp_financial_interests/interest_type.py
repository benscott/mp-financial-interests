import abc


class InterestType:

    __metaclass__ = abc.ABCMeta

    def __init__(self, type_code, title, amount_required=False):
        self.type_code = type_code
        self.title = title
        self.amount_required = amount_required

    @abc.abstractproperty
    def code_of_conduct_year_published(self):
        return None

    def is_code_of_conduct_for(self, session):
        session_start_year = int(session.split('-')[0])
        return session_start_year >= self.code_of_conduct_year_published

    def __repr__(self):
        return '<InterestType {} {}>'.format(self.code_of_conduct_year_published, self.title)


class InterestType2010(InterestType):
    code_of_conduct_year_published = 2010


class InterestType2015(InterestType):
    code_of_conduct_year_published = 2015
