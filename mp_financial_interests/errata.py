import abc
import logging
from mp_financial_interests.lib.helpers import normalise_member_name
from mp_financial_interests.interest_types import interest_types
from mp_financial_interests.erratum import InterestTypeErratum, ParentLineErratum, AmountErratum


logger = logging.getLogger()


class Errata:

    def __init__(self, errata):
        self._errata = {}
        self._error_messages = self._get_error_messages()
        for erratum in errata:
            self.add_erratum(erratum)

    @staticmethod
    def _get_error_messages():
        return {e.error_code: e.error_message for e in [
            InterestTypeErratum, ParentLineErratum, AmountErratum]
        }

    def add_erratum(self, erratum):
        self._errata.setdefault(erratum.error_code, []).append(erratum)

    def get_erratum(self, error_code, filters):
        filters_set = set(tuple(filters.items()))
        for err in self._errata.get(error_code, []):
            # ALl of the erratum filter on values must be present in the
            # supplied filter params for the erratum to be a match
            if err.filter_on.issubset(filters_set):
                return err

    def handle_error(self, error_code, interest, line, **filters):
        filters['line'] = line.text
        erratum = self.get_erratum(error_code, filters)
        if erratum:
            erratum.process_error(interest, line)
            return erratum
        else:
            self._log_error(error_code, filters)
            # print('''
            #     AmountErratum(
            #         member_name="{member_name}", session="{session}", line="{line}"
            #     ),'''.format(member_name=filters.get('member_name'), line=line.text, session=filters.get('session'), ))

    def _log_error(self, error_code, filters):
        message = '{error_message} {member_name} ({session}) - {line}'.format(
            error_message=self._error_messages[error_code],
            **filters
        )
        logger.error(message)


errata = Errata(
    [
        # Some lines have been added as title <h3> etc., but are actually
        # Just normal lines - add here to be ignored
        InterestTypeErratum(member_name='ELLIOTT, Julie',
                            session='2013-14',
                            commit_interest=False,
                            # Weirdly, just another MPs name added in to this one
                            line='ELLIS, Michael (Northampton North)'
                            ),
        InterestTypeErratum(member_name='davies, glyn',
                            line='Self-employed farmer.'),

        ParentLineErratum(member_name='REEVELL, Simon', type_code=2,
                          replacement_line='Barrister in receipt of legal aid payments as follows:'),
        # Intentation all over the place, so just ignore the whole 12-13 / 13-14 session
        ParentLineErratum(member_name='WIGGIN, Bill', session='2013-14'),
        ParentLineErratum(member_name='WIGGIN, Bill', session='2012-13'),
        # Complete mess - ignore all missing parents & amounts
        # This means N Roberts records do not have all the info - but there's no rule that'll
        ParentLineErratum(member_name='neill, robert',
                          session='2014-15', commit_interest=False),
        ParentLineErratum(member_name='lewis, julian',
                          session='2014-15', commit_interest=True, type_code=8),

        # 2010-12
        # AmountErratum(
        #     member_name="clappison, james", session='2010-12', line="Member of Lloyd's. (Resigned 31 December 1994.)"),
        AmountErratum(
            member_name="beresford, paul", session='2010-12', line="Employed as part-time dental surgeon for Beresford Dental Practice Limited."
        ),
        AmountErratum(
            member_name="GRIEVE, Dominic", session='2010-12', line="Ex-member of Lloyds' reinsured into Equitas and a member of NACDE, a Names Action Group."
        ),
        AmountErratum(
            member_name="gove, michael", session='2010-12', line="Contract from Harper Collins to write historical biography."
        ),
        AmountErratum(
            member_name="garnier, edward", session='2010-12', line="Recorder for the Ministry of Justice. Address: Ministry of Justice, 102 Petty France, London, SW1H 9AJ. I shall not sit while a Minister."
        ),
        AmountErratum(
            member_name="freeman, george", session='2010-12', line="Between November 2010 and November 2011 I provided strategic support to the Technology Practice of PA Consulting, Cambridge Technology Centre, Melbourn, Royston, Herts SG8 6DPas part of their taking all client engagement and business development work for 4D Biomedical Ltd (see Category 1 above) on 21 December 2009. (Updated 29 November 2011)"
        ),
        AmountErratum(
            member_name="harris, tom", session='2010-12', line="Contract with Biteback Publishing Ltd, Westminster Tower, 3 Albert Embankment, London SE1 7SP for publication of book. (Registered 13 October 2011)"
        ),
        AmountErratum(
            member_name="hunt, jeremy", session='2010-12', line="(c) Support in the capacity as an MP:"
        ),
        AmountErratum(
            member_name="leigh, edward", session='2010-12', line="Employment ceased 1 June 2011 .",
        ),
        AmountErratum(
            member_name="miliband, david", session='2010-12', line="Senior Advisor to Indus Basin Holdings, from 30 January 2012. Address: No 5, Street 15, Sector F-7/2, Islamabad, Pakistan. Payment on a quarterly basis. (Registered 16 February 2012)",
        ),
        AmountErratum(
            member_name="pickles, eric", session='2010-12', line="Printing of calendars and advice centre notices by International Property Magazine, of Chelmsford.",
        ),
        AmountErratum(
            member_name="opperman, guy", session='2010-12', line="Solicitors: Withy King. Address: Vectis Court, 4-6 Newport Street, Old Town, Swindon SN1 3DX (Registered 18 November 2010)",
        ),
        AmountErratum(
            member_name="skidmore, chris", session='2010-12', line="Author.",
        ),
        AmountErratum(
            member_name='redwood, john', session='2010-12', line="Member of the Advisory Board of EPIC Private Equity, Audrey House, 16-20 Ely Place, London EC1N 6SN. (Registered 7 February 2012)"
        ),
        AmountErratum(
            member_name='REEVELL, Simon', session='2010-12', line='24 January 2012, 3350 plus VAT in respect of one appearance and 3.5 hours work between 10 January 2012 and 24 January 2012. (Registered 20 February 2012)', replacement_amount=3350
        ),
        AmountErratum(
            member_name='williams, roger', session='2010-12', line="Partner in R. H. Williams; a farming partnership. I provide administrative support for the partnership, amounting to less than 3 hours a week."
        ),
        AmountErratum(
            member_name='WICKS, Malcolm', session='2010-12', line="Lectures for Westminster Explained, 4 Grosvenor Place, London SW1X 7DL."
        ),
        AmountErratum(
            # Conversion of Australian dollars to pounds
            member_name='rifkind, malcolm', replacement_amount="6856.67", session='2010-12', line="July 2011: one hour meeting in London. (Updated 30 August 2011)"
        ),



        # 2012-13
        AmountErratum(
            member_name='brooke, annette', session='2012-13', line="Joint owner with my husband of Broadstone Minerals, a small retail and wholesale business dealing in rocks, minerals and gemstones. Address: Broadstone Minerals, 22 Upper Golf Links Road, Broadstone, Dorset, BH18 8BX."
        ),
        AmountErratum(
            member_name='dorrell, stephen', session='2012-13', line="(of Faithful Group Ltd) Celerant Consulting Ltd. (management consultants). Address: Avalon House, 72 Lower Mortlake Road, Richmond, Surrey, TW9 2JY. (Registered 1 August 2012)"
        ),
        AmountErratum(
            member_name='grant, helen', session='2012-13', line="Designated Member of Grants Solicitors LLP, Airport House, Purley Way, Croydon, Surrey CRO 4RE. I occasionally practised as a solicitor and received drawings until September 2012; since that date I have ceased to practise as a solicitor and I no longer receive any share of the profits. (Updated 18 January 2013)"
        ),
        AmountErratum(
            member_name='harris, tom', session='2012-13', line="Payment from Ipsos MORI, 79-81 Borough Road, London SE1 1FY, for completing survey. Hours: 30 mins. (Registered 15 January 2013)"
        ),
        AmountErratum(
            member_name='hemming, john', commit_interest=False, session='2012-13', line="Hours: 4 hours per month in 2012 and additional 4 hours in October 2012. (Registered 11 October 2012)"
        ),
        AmountErratum(
            member_name="vaz, keith", session='2012-13', line="Fee for appearance on 25 March 2013. Hours: 15 mins, plus 2 hrs' travel. (Registered 9 April 2013)"
        ),


        # 2013-14
        AmountErratum(
            member_name="baldry, tony", session="2013-14", line="Practising barrister, arbitrator and mediator."
        ),
        AmountErratum(
            member_name="darling, alistair", session="2013-14", commit_interest=False, line="All fees listed below between 1 May 2011 and 28 May 2013 include VAT. (Registered 24 June 2013)"
        ),
        AmountErratum(
            member_name="elliott, julie", session="2013-14", line="ELLIS, Michael (Northampton North)", commit_interest=False
        ),
        AmountErratum(
            member_name="galloway, george", session="2013-14", line="From 1 April 2013, LBP has paid me for a weekly news show. Address: Westgate House, Hanger Lane, London W5 1YY. (Registered 7 April 2013; updated 10 December 2013)"
        ),
        AmountErratum(
            member_name="grieve, dominic", session="2013-14", line="Ex-member of Lloyds' reinsured into Equitas and a member of NACDE, a Names Action Group."
        ),
        AmountErratum(
            member_name="halfon, robert", session="2013-14", line="Payment received in March 2014 from News UK and Ireland Ltd, PO Box 151, Peterborough PE7 8YT, for article published in May 2013. Hours: 3 hrs. (Registered 7 April 2014)"
        ),
        AmountErratum(
            member_name="hemming, john", session="2013-14", line="I am Senior Partner of JHC (aka John Hemming and Company) LLP, of 1 Temple Row, Birmingham B2 5LG; a software house."
        ),
        AmountErratum(
            member_name="hemming, john", session="2013-14", line="The salary of a member of my staff was paid by Birmingham City Council until June 2013 (Updated 13 September 2013)"
        ),
        AmountErratum(
            member_name="piero, gloria", session="2013-14", line="(a) Donations to my constituency party or association, which have been or will be reported by my party to the Electoral Commission:"
        ),
        AmountErratum(
            member_name="howarth, gerald", session="2013-14", line="Consultant to Blenheim Capital services Ltd of Level 2, 3 Sheldon Square, London W2 6HY. The role involves providing business advice. (Registered 4 June 2013)"
        ),
        AmountErratum(
            member_name="poulter, daniel", session="2013-14", line="Medical doctor"
        ),
        AmountErratum(
            member_name="vaz, keith", session="2013-14", line="Fee for appearance on 27 August 2013. Hours: 15 mins, plus 2 hrs travel. (Registered 10 September 2013)"
        ),

        # 2014-15
        AmountErratum(
            member_name='neill, robert', session='2014-15', commit_interest=False
        ),
        AmountErratum(
            member_name='djanogly, jonathan', session='2014-15', line="Payments received from King & Wood Mallesons LLP (formerly SJ Berwin LLP), 10 Queen Street Place London EC4R 1BE, for consultancy services provided through CGLV Ltd (see entry under Shareholdings below). (Updated 5 November 2014)"
        ),
        # Potentially could be fixed - double line parent entry...
        AmountErratum(
            member_name='dorrell, stephen', commit_interest=False, session='2014-15', line="I provide management consultancy services to the following clients:"
        ),
        AmountErratum(
            member_name='dorrell, stephen', session='2014-15', line="(of Dorson Transform Ltd)"
        ),
        AmountErratum(
            member_name='grieve, dominic', session='2014-15', line="Ex-member of Lloyds' reinsured into Equitas and a member of NACDE, a Names Action Group."
        ),
        AmountErratum(
            member_name='halfon, robert', session='2014-15', line="Payment received in March 2014 from News UK and Ireland Ltd, PO Box 151, Peterborough PE7 8YT, for article published in May 2013. Hours: 3 hrs. (Registered 7 April 2014)"
        ),
        AmountErratum(
            member_name='ottaway, richard', session='2014-15', line="Solicitor and Arbitrator."
        ),
        AmountErratum(
            member_name='watson, tom', session='2014-15', line="Payments relating to the publication of a book I have co-authored, for which I have a contract with Penguin Books, 80 The Strand, London WC2R 0RL. (Registered 14 May 2012)"
        ),


        # 2015/16
        AmountErratum(
            member_name="benyon, richard", session='2015-16', line="From 12 October 2015, Associate Director, Sancroft International Ltd (consultants in corporate responsibility and environmental, social, ethical and planning issues), of 46 Queen Anne's Gate, London, SW1H 9AP. Payment to be made on an ad hoc basis for work done (consultancy services and assistance with obtaining contracts). (Registered 21 October 2015)"
        ),
        AmountErratum(
            member_name='cash, william', session='2015-16', line="Solicitor, William Cash & Co, The Tithe Barn, Upton Cresset, nr Bridgnorth, WV16 6UH."
        ),
        AmountErratum(
            member_name='chapman, douglas', session='2015-16', line="Until 26 June 2015, Spokesperson for COSLA, Verity House, 19 Haymarket Yards, Edinburgh EH12 5BH. (Registered 08 June 2015)"
        ),
        AmountErratum(
            member_name='Dinenage, Caroline', session='2015-16', line="Until end June 2015, Director of Dinenages Ltd, trading as Recognition Express Southern London Road Horndean PO8 0BL, manufacturer of corporate identity products. (Updated 2 July 2015)"
        ),
        AmountErratum(
            member_name="hancock, matthew", session='2015-16', line="Name of donor: Tattersalls Address of donor: 125 Terrace House, High Street, Newmarket, Suffolk CB8 9BS Amount of donation or nature and value if donation in kind: drinks party in aid of West Suffolk fighting fund Donor status: company, registration 00791113 (Registered 28 May 2015)"
        ),
        AmountErratum(
            member_name="hollern, kate", replacement_amount=2000, line="Name of donor: Paperco Ltd Address of donor: Unit 3, Sharples Street, Blackburn Amount of donation or nature and value if donation in kind: 2,000 Date received: 13 April 2015 Date accepted: 13 April 2015 Donor status: company, registration 8454420 (Registered 04 June 2015)"
        ),
        AmountErratum(
            member_name="lewis, clive", replacement_amount=680.05, line="Name of donor: Unite Address of donor: 128 Theobalds Road, Holborn, London WC1X 8TN Amount of donation or nature and value if donation in kind: 23 March 2015, postage, value 680.05 Donor status: trade union (Registered 07 June 2015)"
        ),
        AmountErratum(
            member_name="nally, john", session='2015-16', line="On 1 June 2015, resigned as Councillor for Falkirk Council, Municipal Buildings, Falkirk FK1 5RS. Awaiting final payment. (Registered 08 June 2015)"
        ),
        AmountErratum(
            member_name="stevens, jo", session='2015-16', line="Prior to my election, I practised as a solicitor and was part owner and director of a solicitors firm, Thompsons Solicitors LLP, Congress House, Great Russell Street, London WC1B 3LW, a limited liability partnership. I resigned on 8 May 2015. Between May 2015 and February 2018, I will receive profit share payments attributable to the period up to my departure from the practice. (Registered 5 June 2015; updated 26 October 2015)"
        ),
        AmountErratum(
            member_name="wishart, pete", session='2015-16', line="I receive payments for my published works from the Performing Rights Society."
        ),
        AmountErratum(
            member_name='neill, robert', session='2015-16'),

        # 2016-17
        AmountErratum(
            member_name='neill, robert', session='2016-17'
        ),
        AmountErratum(
            member_name='smith, owen', session='2016-17', replacement_amount=2050, line='Name of donor: Edward Morgan Address of donor: private Amount of donation or nature and value if donation in kind: helping to film a video for my campaign for leadership of the Labour Part, including associated travel and accommodation expenses, value 2,050 Date received: 30 August 2016 Date accepted: 30 August 2016 Donor status: individual (Registered 20 September 2016)'
        ),
        AmountErratum(
            member_name='Stevens, Jo', session='2016-17', line='Prior to my election, I practised as a solicitor and was part owner and director of a solicitors firm, Thompsons Solicitors LLP, Congress House, Great Russell Street, London WC1B 3LW, a limited liability partnership. I resigned on 8 May 2015. Between May 2015 and February 2018, I will receive profit share payments attributable to the period up to my departure from the practice. (Registered 5 June 2015; updated 26 October 2015)'
        ),

        # 2017-19
        AmountErratum(
            member_name='cruddas, jon', session='2017-19', replacement_amount=150, line='Received on 29 September 2017, payment of 150. Hours: 90 mins. (Registered 13 November 2017)'
        ),
        AmountErratum(
            member_name='jones, darren', line='From 3 October 2017 I am contracted to provide legal consultancy, via the office of Darren Jones Ltd, to Kemp Little LLP, 138 Cheapside, London EC2V 6BJ. (Registered 19 October 2017)'
        ),
        AmountErratum(
            member_name='neill, robert', session='2017-19'
        ),
        AmountErratum(
            member_name='whitford, philippa', session='2017-19', line="Locum Consultant Breast Cancer Surgeon for Ayrshire & Arran Health Board, Eglinton House, Ailsa Hospital, Dalmellington Road, Ayr KA6 6AB. (Registered 08 December 2015)"
        ),
        AmountErratum(
            member_name='chope, christopher', session='2017-19', line='Director of Carclew Limited; small private company which provides business consultancy services but excludes advice on parliamentary or public affairs. (Updated 20 June 2017)'
        ),

        # Errors repeating across multiple sessions - so these do not have a session specified
        AmountErratum(
            member_name='bellingham, henry', line="Former member of Lloyds (resigned 1999. Reinsured into Equitas.)"
        ),
        AmountErratum(
            member_name='Buckland, Robert', line="Queen's Counsel."
        ),
        AmountErratum(
            member_name='Bone, Peter', line='Owner of PWB Accountants, 40 Chester Road, Wellingborough, Northants NN8 1NY. (Registered 15 April 2016)'
        ),
        AmountErratum(
            member_name='clappison, james', line="Member of Lloyd's. (Resigned 31 December 1994.)"
        ),
        AmountErratum(
            member_name="Cherry, Joanna", line="As a QC and member of the Faculty of Advocates, I will continue to receive payments for legal services rendered before my election. (Registered 04 June 2015)"
        ),
        AmountErratum(
            member_name='dorrell, stephen', commit_interest=False, line="Kandahar Asset Management Company Ltd, Nuffield House, 41-46 Piccadilly, London W1J 0DS. (Registered 5 July 2013)"
        ),
        AmountErratum(
            member_name='dorrell, stephen', commit_interest=False, line="Celerant Consulting Ltd. (management consultants). Address: Avalon House, 72 Lower Mortlake Road, Richmond, Surrey, TW9 2JY. (Registered 1 August 2012)"
        ),
        AmountErratum(
            member_name='djanogly, jonathan', line="Membership of Lloyds (resigned 31 December 2006)."
        ),
        AmountErratum(
            member_name='ellwood, tobias', line='Ongoing service in the Territorial Army. Payments are received from the Army Pay Office, 65 Brown St, Glasgow G2 8EX.'
        ),
        AmountErratum(
            member_name='fox, liam', line='Contract with Quercus Editions Limited for writing a book. Address: Quercus Editions Limited, 55 Baker Street, 7th Floor, South Block, London, W1U 8EW.'
        ),
        AmountErratum(
            member_name='galloway, george', line="Of Molucca Media Ltd:"
        ),
        AmountErratum(
            member_name='harrison, trudy', line='Sole trader providing administrative and project management support to FNS Ltd, private investors, of The Old Vicarage, Lock, Carnforth, Lancs. (Registered 22 March 2017)'
        ),
        AmountErratum(
            member_name='hemming, john', line="The salary of a member of my staff is paid by Birmingham City Council."
        ),
        AmountErratum(
            member_name="howarth, gerald", line="Consultant to Blenheim Capital Services Ltd of Level 2, 3 Sheldon Square, London W2 6HY. The role involves providing business advice. (Registered 04 June 2013)"
        ),
        AmountErratum(
            member_name="howarth, gerald", line="Consultant to Sigma Energy, Castle Acre Industrial Estate, Swaffham, PE37 7HY. The role involves providing business advice. (Registered 02 September 2013)"
        ),
        # Ignore this one - it's just an addition to the previous interest
        AmountErratum(
            member_name="kawczynski, daniel", line="Arrangement terminated June 2012. (Updated 19 June 2012)", commit_interest=False
        ),
        AmountErratum(
            member_name='leigh, edward', line="Barrister at Law."
        ),
        AmountErratum(
            member_name="ottaway, richard", line="Solicitor and Arbitrator."
        ),
        AmountErratum(
            member_name="mcdonnell, alasdair", line="Member of the Northern Ireland Assembly, Parliament Buildings, Stormont, Belfast.",
        ),
        AmountErratum(
            member_name='pritchard, mark', line='Director of Mark Pritchard Advisory Ltd, c/o Gallaghers, 2nd Floor, 69/85 Tabernacle Street, London EC2A 4RR. (Registered 7 September 2013; updated 7 July 2015)'
        ),
        AmountErratum(
            member_name='rees-mogg, jacob', line='As a client of Somerset Capital Management (SCM), I provide services to The Chestnut Fund, an investment fund. (Registered 27 November 2012)'
        ),
        AmountErratum(
            member_name="rees-mogg, jacob", line="Redwood Emerging Markets Dividend Income Fund, Adelaide Street West, Suite 2400 P.O. Box 23, Toronto, Ontario, M5H 1T1."
        ),
        AmountErratum(
            member_name="sheerman, barry", line="Member of Environmental Scrutiny Board of Veolia Environmental Services (UK) plc; environmental waste management company. Address: Veolia House, 154a Pentonville Road, London, N1 9PE. Work includes attending meetings and providing advice on environmental issues."
        ),
        AmountErratum(
            member_name='wishart, peter', line="I receive payments for my published works from the Performing Rights Society."
        ),
        AmountErratum(
            member_name='tredinnick, david', line="Member of Lloyd's."
        ),
        AmountErratum(
            member_name="baker, norman", line="Ongoing income from royalties for publication of book entitled 'The Strange Death of David Kelly'"
        ),
        AmountErratum(
            member_name='zahawi, nadhim', type_code=3
        ),
        AmountErratum(
            member_name='zahawi, nadhim', line="YouGov Plc; research and consulting. Address: 50 Featherstone Street, London EC1Y 8RT"
        ),
        AmountErratum(
            # No value attached to any of the clients: https://publications.parliament.uk/pa/cm/cmregmem/130422/walker_robin.htm
            member_name="walker, robin", type_code=3
        ),

    ]
)
