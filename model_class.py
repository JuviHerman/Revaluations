import numpy as np
import pandas as pd
from typing import List, Optional, Dict
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)
from convex_class import RnpdEquation
from data_classes import M
from const import EXPECTED_DATA_COLUMNS


class ModelData:
    def __init__(self):
        self.data: Dict[str, pd.DataFrame] = {}
        # each item in the dict is perpetualy updating a
        # group class of type M. groups are ranging between 1-12
        self.classes: Dict[int, M] = {}
        # each month is keeping a track of its own data for model calculation
        self.models_data: Dict[str, pd.DataFrame] = {}
        # each month has its own model calculated on "gold distribution"
        self.models: Dict[str, RnpdEquation] = {}


    @staticmethod
    def check_input_data(data: pd.DataFrame) -> bool:
        return all([col in EXPECTED_DATA_COLUMNS for col in data.columns])

    def load_month(self, data: pd.DataFrame, month: str):
        # param1: data - df containing columns:
        # param2: month
        # Iterate over unique classes (M)  & durations (x) in the DataFrame and load to class

        if not self.check_input_data(data):
            print(f'data input is not with the expected columns:\n{EXPECTED_DATA_COLUMNS}')
            exit()

        self.data[month] = data

        for m in sorted(data['M'].unique()):
            df = data[data['M']==m]
            if not df.empty:
                if not m in self.classes.keys():
                    self.classes[m] = M(m)
                self.classes[m].update_items(df)
                self.models_data[month] = self.fit_current_data_to_df()

    def fit_current_data_to_df(self)\
            -> Optional[pd.DataFrame]:
        df = []
        for group_index, m_class in sorted(self.classes.items()):
            for duration_index, duration_class in sorted(m_class.durations.items()):
                d = {'group_index': group_index,
                     'duration_index': duration_index,
                     'rnpd': np.median([sample.y for sample in duration_class.samples])
                     }
                df.append(d)
        if len(df) > 0:
            return pd.DataFrame(df)
        else:
            return None

    def add_monthly_model(self, month: str):
        if not self.models_data[month].empty:
            self.models[month] = RnpdEquation(data=self.models_data[month],
                                              month=month)
            self.models[month].fit_polynomial_regression()
        else:
            print(f'Month: {month} has not data to load')


    def plot_monthly_model(self, month: str):
        if month in self.models:
            self.models[month].plot_graphs()
        else:
            print(f'Month: {month} was not calculated for a model')


    def predict_class(self,
                      month: str,
                      data: pd.DataFrame):
        pred_model: Optional[RnpdEquation]
        try:
            pred_model = self.models[month]
            if pred_model:
                return data.apply(lambda x: pred_model.get_matching_group(x['x'], x['y']), axis=1)
        except KeyError:
            print(f'Month {month} was not calculated for a model')



