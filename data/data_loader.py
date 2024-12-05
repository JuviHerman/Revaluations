import logging
import pandas as pd
import numpy as np
from typing import Optional
from data.const import (PROSPECTUS_COLUMNS, RANKED_DATA_RELEVANT_COLUMNS, HAZARD_RATE_COL,
                   AMIHOOD_LIQUIDITY_COLUMN, RANK_COLUMN, GOLDEN_DISTRIBUTION_FILTER_COLUMNS,
                   GOLDEN_DISTRIBUTION_CONDITIONS, GOV_FILE_PATH, SEC_FILE_PATH, PROSPECTUS_FILE,
                   GOV_SAMPLE_SIZE
                   )
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
import matplotlib.pyplot as plt

class Loader:

    def __init__(self):
        self.secs: Optional[pd.DataFrame] = None
        self.gov: Optional[pd.DataFrame] = None
        self.full_dataset: Optional[pd.DataFrame] = None
        self.is_loading_successful: bool = False
        self.is_prospectus_updated: bool = False
        self.is_liquidity_calculated: bool = False
        self.is_net_hazard_rate_updated: bool = False

    def load_ranked_data(self,
                         gov_file_path: str = GOV_FILE_PATH,
                         sec_file_apath: str = SEC_FILE_PATH)\
    -> [pd.DataFrame, pd.DataFrame]:
        try:
            secs = pd.read_excel(sec_file_apath)
            gov = pd.read_excel(gov_file_path)

            '''set ranks from originals columns according to business logic (gov = best rank = 1)'''

            secs['RankID'] = secs[RANK_COLUMN]
            gov['RankID'] = 1

            ''' 
            filtering rows with null value - all required for RNPD:
            #   1. RankID - between 1-28
            #   2. HAZARD_RATE per-calculated
            #   3. liquidity score
            '''

            gov = gov[(~gov[HAZARD_RATE_COL].isnull()) &
                      (~gov[AMIHOOD_LIQUIDITY_COLUMN].isnull())]

            secs = secs[(~secs[RANK_COLUMN].isnull()) &
                        (~secs[HAZARD_RATE_COL].isnull()) &
                        (~secs[AMIHOOD_LIQUIDITY_COLUMN].isnull())]

            '''fetch relevant columns only'''

            self.secs = secs[RANKED_DATA_RELEVANT_COLUMNS]
            self.gov = gov[RANKED_DATA_RELEVANT_COLUMNS]
            self.is_loading_successful = True

        except Exception as e:
            logging.error("Error occurred during loading of ranked data: %s", e)


    def add_prospectus_data(self,
                            prospectus_path: str = PROSPECTUS_FILE['path'],
                            sheet_name: str = PROSPECTUS_FILE['sheet']):

        try:
            secs = self.secs.copy()
            prospectus = pd.read_excel(prospectus_path, sheet_name)
            secs = secs.merge(prospectus[PROSPECTUS_COLUMNS], on=['SecurityID'], how='left')

            '''filling missing data when known for each Security'''
            secs[GOLDEN_DISTRIBUTION_FILTER_COLUMNS] = secs.sort_values('ReportDate').groupby('SecurityID')\
                [GOLDEN_DISTRIBUTION_FILTER_COLUMNS].transform(lambda x: x.ffill())

            self.secs = secs
            self.is_prospectus_updated = True

        except Exception as e:
            logging.error("Error occurred during load or merge of prospectus data: %s", e)

    @staticmethod
    def get_monthly_mean_yield(x: pd.DataFrame):
        if x.shape[0] <= 3:
            return None
        else:
            samples = x.shape[0] // 3
            upper = x.sort_values(by=AMIHOOD_LIQUIDITY_COLUMN, ascending=False)['YieldBruto'].head(samples).median()
            lower = x.sort_values(by=AMIHOOD_LIQUIDITY_COLUMN, ascending=False)['YieldBruto'].tail(samples).median()
            return (upper - lower).round(3)


    @staticmethod
    def get_ami_means(df: pd.DataFrame):
        df = df[df[AMIHOOD_LIQUIDITY_COLUMN] < df[AMIHOOD_LIQUIDITY_COLUMN].quantile(0.99)].copy()
        df['duration'] = np.round(df['DurationBruto'])
        df.drop_duplicates(subset=['month', 'SecurityID'], keep='first', inplace=True)
        df = df.groupby(['RankGroup', 'month']).apply(lambda x: Loader.get_monthly_mean_yield(x))
        return df


    def add_liquidity_premium(self):
        try:
            # add liquidity
            secs = self.secs.copy()
            secs['RankGroup'] = np.where(secs['RankID'].between(1, 5), 1,
                                    np.where(secs['RankID'].between(6, 10), 2, 3))
            secs['month'] = secs['ReportDate'].dt.to_period('M')
            ami_means = Loader.get_ami_means(secs)
            secs['liquidity_premium_ami'] = secs.set_index(['RankGroup', 'month']).index.map(ami_means).fillna(0)
            secs['liquidity_premium_ami'] = np.clip(secs['liquidity_premium_ami'], 0, None)
            secs.drop('RankGroup', axis=1, inplace=True)
            self.secs = secs
            self.is_liquidity_calculated = True

            # build net hazard rate
            self.secs['Net Hazard Rate'] = self.secs[HAZARD_RATE_COL] - self.secs['liquidity_premium_ami']
            self.is_net_hazard_rate_updated = True

            #  fill value in new columns in gov as well
            self.gov['Net Hazard Rate'] = self.gov[HAZARD_RATE_COL]
            self.gov['month'] = self.gov['ReportDate'].dt.to_period('M')

        except Exception as e:
                logging.error("Error occurred during liquidity premium calculation: %s", e)

    def build_full_dataset(self):
        try:
            self.gov['GuaranteeID'] = 0
            self.gov['NegativePledgeID'] = 0
            self.gov['SeniorityID'] = 1

            self.full_dataset = pd.concat([self.gov.sample(GOV_SAMPLE_SIZE, replace=True),
                                           self.secs]).dropna(subset=['DurationBruto','Net Hazard Rate'])

        except Exception as e:
            logging.error("Error occurred during concatenation gov and secs to a full dataframe: %s", e)


    def calculate_rnpd(self):
        try:
            self.full_dataset['M'] =\
                np.where(self.full_dataset['RankID'].between(12, 23), 11,
                  np.where(self.full_dataset['RankID'] >= 24, 12,
                    self.full_dataset['RankID']))

            rnpd_dictionary = self.full_dataset.groupby(['SecurityID', 'month']).apply(lambda x: \
                1 - np.exp(-x['Net Hazard Rate'].mean() / 10), include_groups=False)

            self.full_dataset['RNPD'] = self.full_dataset.apply\
                (lambda x: rnpd_dictionary[(x.SecurityID, x.month)], axis=1)

            #  override protocol definitions in this calculation
            self.full_dataset.loc[self.full_dataset['RankID'] == 1, 'RNPD'] = 0  #  gov
            self.full_dataset.loc[self.full_dataset['RankID'] >= 24, 'RNPD'] = 1  # defaulted

            print(self.full_dataset.shape)
            self.full_dataset['RNPD'].plot.hist(bins=30, title='RNPD')
            plt.show()

        except Exception as e:
            logging.error("Error occurred during RNPD calculation: %s", e)

def main_handler():
    loader = Loader()
    loader.load_ranked_data(gov_file_path=GOV_FILE_PATH,
                            sec_file_apath=SEC_FILE_PATH)
    if loader.is_loading_successful:
        loader.add_prospectus_data(prospectus_path=PROSPECTUS_FILE['path'],
                                   sheet_name=PROSPECTUS_FILE['sheet'])
        if loader.is_prospectus_updated:
            loader.add_liquidity_premium()
            if loader.is_liquidity_calculated and loader.is_net_hazard_rate_updated:
                loader.build_full_dataset()
                loader.calculate_rnpd()


if __name__ == '__main__':
    main_handler()