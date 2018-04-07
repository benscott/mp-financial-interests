MP Financial Interests
======================

Python script for parsing data from the UK House of Commons Register of Members' Financial Interests http://www.publications.parliament.uk/pa/cm/cmregmem/contents1415.htm.

[![codecov](https://codecov.io/gh/benscott/mp-financial-interests/branch/master/graph/badge.svg)](https://codecov.io/gh/benscott/mp-financial-interests)


Overview
--------

Written for [mpreportcard.co.uk (offline)](http://www.mpreportcard.co.uk), to provide an overview of MPs for the 2015 General Election.

The 2010-2018 data can be downloaded from: [https://github.com/sparkd/mp-financial-interests](https://github.com/sparkd/mp-financial-interests)


The following information is extracted:

| Field        | Description | 
| ------------ |-------------| 
| Member name  | The name of the Member of Parliament (honorifics removed) | 
| Title        | Interest type title e.g Employment and earnings |
| Type code    | Numeric type code 1-10, denoting interest type.  Important note: the codes changed in 2015.  So Employment and earnings has code 2 in sessions before 2015; code 1 in post-2015 sessions.) |
| Amount       | The registered amount of the interest, in pounds.  |
| Date         | The registered date of the interest (not necessarily the actual date of the interest) |
| Description  | Full description of the interest, extracted directly from register. |
| Session      | The parliamentary session the interest is included in - e.g. 2010-12; 2015-16 |


CLI Commands
------------

A command line interface is provided.

```sh
  python cli.py [OPTIONS]
```

With the following options:

- `--session -s` Processs interest for a particular session e.g. 2010-12
- `--member-name -mp` Processs specific member e.g. "Abbot, Diane"
- `--filter -f` Filter interest descriptions
- `--output -o` Output to console or CSV (/tmp/mps.csv)
- `--group_by -g` Group interests by member, session or both.
- `--order` Order interests by field - e.g. amount to see MPs with highest interest amount
- `--clear_cache -cc` Clear cache - do not used cached data
- `--verbosity` [Click log](https://github.com/click-contrib/click-log) debug verbosity


#### Examples

Display all interests for Norman Baker in console:


```sh
  python cli.py  --verbosity INFO -o console -mp "BAKER, Norman"
```


Display total for all MPs in the 2014-15 session in console:


```sh
  python cli.py  --verbosity INFO -s 2014-15 -o console -g mp
```

Output all interests to CSV (`/tmp/mps.csv`):


```sh
  python cli.py  --verbosity INFO -o csv
```

Show all interests with "cornwall" in the description, ordered by amount:


```sh
  python cli.py  --verbosity INFO -f "cornwall" -o console --order amount
```


Assumptions & limitations
-------------------------

The published interests data isn't uniformally structured, so source records should be checked for confirmation.

There are also some known issues with the scripts:

- Only parses information from 2010-2018 Registers. For Members' Financial Interests prior to 2010, the format changes substantially. 

- It does not handle recuring/repeat payments. For example, [RIFKIND, Rt Hon Sir Malcolm](https://publications.parliament.uk/pa/cm/cmregmem/120430/rifkind_malcolm.htm) records interest "Monthly ongoing payment of £4,666.66"  (14 February 2011). But this will be extracted as a single entry of £4,666.66.  See TODO.

- When there are mutliple values in a line, the highest value will be preferred. This is based on the assumption that interests include a summary and a total. However this isn't correct 100% of the time.  

- Some interests include the numeration band of the interest e.g. £5,001-£10,000.  When extracting the interest amount, this script prefers non-numeration band values.  If no other value is found, the script will use the numeration band, selecting the uppermost value. 

- Many interests do not record a numeric amount, these are recorded with a zero amount.

- The amount of all interests are in £ pounds.  One known entry ([Malcolm Rifkind, 30 August 2011](https://publications.parliament.uk/pa/cm/cmregmem/120430/rifkind_malcolm.htm)) is recorded in Australian dollars and has been converted to pound sterling. See TODO.


Tests
-----

```sh
  nosetests --with-coverage --cover-package mp_financial_interests
```


TODO
----

- Handle recurring payments (NLP?).
- Support multiple currencies


