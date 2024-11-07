from model_class import ModelData
import pandas as pd


def load(data: pd.DataFrame):
    model = ModelData()
    months = sorted(data.month.astype(str).unique())
    for month in months:
        try:
            model.load_month(data=data[data.month == month],
                             month=month)
            model.add_monthly_model(month=month)
            print(f'month: {month} loaded and model calculated')
        except Exception as E:
            print(f'Exception during data parsing of month: {month}')
            print(E)
            pass
    return model


def predict(model: ModelData,
            df: pd.DataFrame):
    months = sorted(df.month.astype(str).unique())
    results = []
    for month in months[1:]:
        x_test = df[df['month'] == month].copy()
        x_test['M_pred'] = model.predict_class(month=str(pd.to_datetime(month).to_period('M') - 1),
                                               data=x_test)
        results.append(x_test)
        print(f'month: {month} data was predicted')
    return pd.concat(results)


def main():

    #  create monthly equations using golden distribution
    golden_distribution_df = pd.read_csv('data/data_for_convex.csv').drop('Unnamed: 0', axis=1)
    golden_distribution_df.rename(columns={'RankID1': 'RankID'}, inplace=True)
    model = load(data=golden_distribution_df)

    #  predict the latest duration/rnpd per Security on last month's model (and save results)
    full_data = pd.read_csv('data/full_data_for_convex.csv').drop('Unnamed: 0', axis=1)
    results = predict(model=model,
                      df=full_data)
    #  save to file
    results.to_csv('~/Desktop/predicted_data.csv')


if __name__ == '__main__':
    main()
