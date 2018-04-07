import click
import click_log
import logging


from mp_financial_interests.register.index import RegisterIndexPage
from mp_financial_interests.interests import Interests


logger = logging.getLogger()
click_log.basic_config(logger)


index = RegisterIndexPage()


@click.command()
@click.option('--session', '-s', default=None, type=click.Choice(index.keys()), help="Import specfic annual period.")
@click.option('--member-name', '-mp', default=None, help='Import specific member.')
@click.option('--filter', '-f', default=None, help='Filter interests by term.')
@click.option('--output', '-o', default=None, type=click.Choice(['csv', 'console']), help="Import specfic annual period.")
@click.option('--group_by', '-g', default=None, type=click.Choice(['mp', 'session']), help="Group interests by member, session or both.", multiple=True)
@click.option('--order', default=None, type=click.Choice(Interests.columns), help="Order interests by field.")
@click.option('--clear_cache', '-cc', is_flag=True)
@click_log.simple_verbosity_option(logger)
def main(session, member_name, filter, output, clear_cache, group_by, order):
    interests = Interests(session, member_name, clear_cache)

    if 'mp' in group_by:
        interests.group_by_member()
    if 'session' in group_by:
        interests.group_by_session()

    if filter:
        interests.set_filter(filter)

    if order:
        interests.set_order_by(order)

    if output == 'csv':
        interests.to_csv('/tmp/mps.csv')
    elif output == 'console':
        print(interests.to_table())
        if interests.total:
            print('TOTAL: £{:0,.2f}'.format(interests.total))


if __name__ == '__main__':
    main()
