from setuptools import setup, find_packages

version = '0.1'

setup(
    name='MPFinancialInterests',
    version=version,
    description="MP Financial Interests",
    long_description="""Script for parsing data from the UK House of Commons Register of Members' Financial Interests """,
    keywords='',
    author='Ben Scott',
    author_email='ben@benscott.co.uk',
    url='https://github.com/benscott/mp-financial-interests',
    license='GNU GPL 3',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'beautifulsoup4',
        'click',
        'click-log',
        'html5lib',
        'pandas',
        'requests',
        'requests-cache',
        'tables'
    ],
    entry_points="""""",
)
