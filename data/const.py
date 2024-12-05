import os

PROSPECTUS_COLUMNS = ['SecurityID','GuaranteeID', 'NegativePledgeID', 'SeniorityID']

RANK_COLUMN = 'MaalotSecurityRankID' # or MidroogSecurityRankID
AMIHOOD_LIQUIDITY_COLUMN = 'AmihudIlliquidityMeasure1' # or AmihudIlliquidityMeasure2
HAZARD_RATE_COL = 'HR_RR'

RANKED_DATA_RELEVANT_COLUMNS = ['ReportDate', 'SecurityID','IssuerName','IssuerSuperSectorName',
                                'PriceClose', 'YieldBruto','DurationBruto', 'ZSpread',
                                RANK_COLUMN, 'RankID',
                                AMIHOOD_LIQUIDITY_COLUMN, HAZARD_RATE_COL
                                ]

GOLDEN_DISTRIBUTION_FILTER_COLUMNS = ['NegativePledgeID', 'GuaranteeID', 'SeniorityID']

GOLDEN_DISTRIBUTION_CONDITIONS = lambda df: (df['NegativePledgeID'] == 0) & (df['GuaranteeID'] == 0)\
                                            & (df['SeniorityID'] == 1)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOV_FILE_PATH = os.path.join(BASE_DIR, 'data', 'originals', 'RNPD_2016-2023_GOV.xlsx')
SEC_FILE_PATH = os.path.join(BASE_DIR, 'data', 'originals', 'RNPD_2016-2023_CorpCPI.xlsx')
PROSPECTUS_FILE = {'path': os.path.join(BASE_DIR, 'data', 'originals', 'prospectus', 'CorpCPI.xlsx'),
                   'sheet': 'Corp CPI prospectus'}

GOV_SAMPLE_SIZE = 2000