from typing import Optional

from model_class import ModelData
import pandas as pd
import matplotlib.pyplot as plt


def testing_checking_pipe(data: pd.DataFrame):
    model = ModelData()
    months = sorted(data.month.unique())
    for month in months:
        print(f'month: {month}')
        model.load_month(data[data.month==month], month)
        df = model.models_data[month].copy()
        if month == months[7]:  #  test only 1 month plots
            fig,ax = plt.subplots()
            print(df)
            for group in sorted(df['group_index'].unique()):
                (df[df['group_index']==group].groupby('duration_index').rnpd.mean().
                 plot(ax=ax, label=group))
            plt.legend(bbox_to_anchor=(1, 1), loc=1, borderaxespad=0)
            plt.grid()
            plt.show()
            break


def testing_loading_to_convex(data: pd.DataFrame):
    model = ModelData()
    months = sorted(data.month.unique())
    for month in months[:50]:
        print(f'month: {month}')
        model.load_month(data[data.month == month], month)
        if month == months[40]:  # test only 1 month plots
            model.add_monthly_model(month)
            model.models[month].plot_graphs()
            break

def testing_getting_model_scores(data: pd.DataFrame):
    model = ModelData()
    months = sorted(data.month.astype(str).unique())
    for month in months:
        print(f'month: {month} loaded')
        model.load_month(data[data.month == month], month)
        model.add_monthly_model(month)
        if month == months[44]:
            test = model.data[month][['M','x','y']].copy()
            test['M_pred'] = model.predict_class(month=str(pd.to_datetime(month).to_period('M')-1),
                                                 data=test)
            print(test[['M','M_pred']])
            break


def main():
    data = pd.read_csv('../data/preprocessed/data_for_convex.csv').drop('Unnamed: 0', axis=1)
    data.rename(columns={'RankID1':'RankID'},inplace=True)
    # testing_checking_pipe(data)  #  check few months to see the class/ mean_rnpd making sense
    testing_loading_to_convex(data)  # check convex works
    # testing_getting_model_scores(data)  #  check convex results scores

if __name__ == '__main__':
    main()