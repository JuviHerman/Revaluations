PROSPECTUS_COLUMNS = ['SecurityID','GuaranteeID', 'NegativePledgeID', 'SeniorityID']
RANKED_DATA_RELEVANT_COLUMNS = ['SecurityID','ReportDate','IssuerName','IssuerSuperSectorName',
                                'FixedAnnualCoupon','PriceClose', 'YieldBruto','DurationBruto',
                                'ZSpread','AmihudIlliquidityMeasure1', 'HR', 'RankID1', 'RankID2']
AMIHOOD_LIQUIDITY_COLUMN = 'AmihudIlliquidityMeasure1'
RANK_COLUMN = 'RankID1'
GOLDEN_DISTRIBUTION_FILTER_COLUMNS = ['NegativePledgeID', 'GuaranteeID', 'SeniorityID']
GOLDEN_DISTRIBUTION_CONDITIONS = lambda df: (df['NegativePledgeID'] == 0) & (df['GuaranteeID'] == 0)\
                                            & (df['SeniorityID'] == 1)

SEC_FILE_PATH = 'originals/RNPD_2016-2023_CorpCPI.xlsx'
GOV_FILE_PATH = 'originals/RNPD_2016-2023_GOV.xlsx'
PROSPECTUS_FILE = {'path': 'originals/prospectus/CorpCPI.xlsx',
                   'sheet': 'Corp CPI prospectus'}
GOV_SAMPLE_SIZE = 2000