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
    url='',
    license='',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'html5lib',
        'requests'
    ],
    entry_points="""""",
)
