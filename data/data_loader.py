import logging
import pandas as pd
import numpy as np
from typing import Optional
from const import (PROSPECTUS_COLUMNS, RANKED_DATA_RELEVANT_COLUMNS,
                   AMIHOOD_LIQUIDITY_COLUMN, RANK_COLUMN, GOLDEN_DISTRIBUTION_FILTER_COLUMNS,
                   GOLDEN_DISTRIBUTION_CONDITIONS
                   )

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')


def load_ranked_data(gov_file_path: str = 'originals/RNPD_2016-2023_CorpCPI.xlsx',
                   sec_file_apath: str = 'originals/RNPD_2016-2023_GOV.xlsx')\
        -> [pd.DataFrame, pd.DataFrame]:
    try:
        secs = pd.read_excel(gov_file_path)
        gov = pd.read_excel(sec_file_apath)

        # set ranks from originals columns according to business logic
        secs['RankID1'] = secs['MidroogSecurityRankID']
        secs['RankID2'] = secs['MaalotSecurityRankID']
        gov['RankID1'] = 1
        gov['RankID2'] = 1
        return secs[RANKED_DATA_RELEVANT_COLUMNS], gov[RANKED_DATA_RELEVANT_COLUMNS]
    except Exception as e:
        logging.error("Error occurred during loading of ranked data: %s", e)


def add_prospectus_data(df: pd.DataFrame,
                        prospectus_path: str = 'originals/prospectus/CorpCPI.xlsx',
                        sheet_name: str = 'Corp CPI prospectus') -> Optional[pd.DataFrame]:

    try:
        prospectus = pd.read_excel(prospectus_path, sheet_name)
        df = df.merge(prospectus[PROSPECTUS_COLUMNS], on=['SecurityID'], how='left')

        '''filling missing data when known for each Security'''
        df[GOLDEN_DISTRIBUTION_FILTER_COLUMNS] = df.sort_values('ReportDate').groupby('SecurityID')\
            [GOLDEN_DISTRIBUTION_FILTER_COLUMNS].transform(lambda x: x.ffill())

        return df
    except Exception as e:
        logging.error("Error occurred during DataFrame load or merge: %s", e)


def get_monthly_mean_yield(x: pd.DataFrame):
    if x.shape[0] <= 3:
        return None
    else:
        samples = x.shape[0] // 3
        upper = x.sort_values(by=AMIHOOD_LIQUIDITY_COLUMN, ascending=False)['YieldBruto'].head(samples).median()
        lower = x.sort_values(by=AMIHOOD_LIQUIDITY_COLUMN, ascending=False)['YieldBruto'].tail(samples).median()
        return (upper - lower).round(3)


def get_ami_means(df: pd.DataFrame):
    df = df[df[AMIHOOD_LIQUIDITY_COLUMN] < df[AMIHOOD_LIQUIDITY_COLUMN].quantile(0.99)].copy()
    df['duration'] = np.round(df['DurationBruto'])
    df.drop_duplicates(subset=['month', 'SecurityID'], keep='first', inplace=True)
    df = df.groupby(['RankGroup', 'month']).apply(lambda x: get_monthly_mean_yield(x))
    return df


def add_liquidity_premium(df: pd.DataFrame):
    df['RankGroup'] = np.where(df[RANK_COLUMN].between(1, 5), 1,
                            np.where(df[RANK_COLUMN].between(6, 10), 2, 3))
    df['month'] = df['ReportDate'].dt.to_period('M')
    ami_means = get_ami_means(df)
    df['liquidity_premium_ami'] = df.set_index(['RankGroup', 'month']).index.map(ami_means)
    df.fillna({'liquidity_premium_ami': 0}, inplace=True)
    df['liquidity_premium_ami'] = np.clip(df['liquidity_premium_ami'], 0, None)
    df.drop('RankGroup', axis=1, inplace=True)
    return df


def main_handler():
    secs, gov = load_ranked_data()
    if not secs.empty and not gov.empty:
        secs_prospectus = add_prospectus_data(df=secs)
        if not secs_prospectus.empty:
            secs_prospectus_liquidity = add_liquidity_premium(df=secs_prospectus)
            print(secs_prospectus_liquidity.head(5))
            print(secs_prospectus_liquidity.shape)


if __name__ == '__main__':
    main_handler()