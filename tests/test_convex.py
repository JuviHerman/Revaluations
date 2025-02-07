from model_class import ModelData
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def test_checking_pipe(data: pd.DataFrame):
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


def test_loading_to_convex(data: pd.DataFrame):
    model = ModelData()
    months = sorted(data.month.unique())
    for month in months[:30]:
        print(f'month: {month} loaded')
        model.load_month(data[data.month == month], month)
        if month == months[9]:  # test only 1 month plots
            model.add_monthly_model(month)
            model.models[month].plot_graphs(month)
            break

def test_plot_all_months(data: pd.DataFrame):
    plt.ion()
    fig, ax = plt.subplots()

    model = ModelData()
    months = sorted(data.month.unique())
    x_vals = np.linspace(0, 10, 100)

    for month in months:
        model.load_month(data[data.month == month], month)
        model.add_monthly_model(month)
        ax.clear()
        for group in sorted(model.models[month].groups.keys()):
            poly_vals = sum([model.models[month].coeffs[group][i] * x_vals ** i for i in range(model.models[month].poly_degree + 1)])
            ax.plot(x_vals, poly_vals, label=f'Group {group}')
        ax.set_ylabel('RNPD')
        ax.set_xlabel('Duration Index')
        ax.set_title(f'{month} - Polynomial Regression for Risk Groups')
        ax.legend(loc='upper left', bbox_to_anchor=(1, 0.5))
        plt.draw()
        plt.pause(0.01)
    plt.ioff()
    plt.show()


import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd


def test_plot_all_months_animation(data: pd.DataFrame, output_file="my_animation.gif"):
    plt.ioff()
    fig, ax = plt.subplots(figsize=(6, 4))
    model = ModelData()
    months = sorted(data['month'].unique())
    x_vals = np.linspace(0, 10, 100)

    def init_func():
        ax.clear()
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 1)
        return []

    def update(frame):
        ax.clear()
        month = months[frame]
        model.load_month(data[data['month'] == month], month)
        model.add_monthly_model(month)

        for group in sorted(model.models[month].groups.keys()):
            coeffs = model.models[month].coeffs[group]
            degree = model.models[month].poly_degree
            # Evaluate polynomial at x_vals
            poly_vals = sum(coeffs[i] * x_vals ** i for i in range(degree + 1))
            ax.plot(x_vals, poly_vals, label=f'Group {group}')

        ax.set_ylabel('RNPD')
        ax.set_xlabel('Duration Index')
        ax.set_title(f'{month} - Polynomial Regression for Risk Groups')

        ax.legend(loc='upper left', bbox_to_anchor=(1, 0.5))
        return []

    ani = animation.FuncAnimation(
        fig, update,
        init_func=init_func,
        frames=len(months),
        interval=1000,
        blit=False
    )

    ani.save(output_file, writer='imagemagick', fps=2)

    print(f"Animation saved to {output_file}")


def test_getting_model_scores(data: pd.DataFrame):
    model = ModelData()
    months = sorted(data.month.astype(str).unique())
    for month in months:
        print(f'month: {month} loaded')
        model.load_month(data[data.month == month], month)
        model.add_monthly_model(month)
        if month == months[5]:
            test = model.data[month][['M','Duration','Rnpd']].copy()
            test['M_pred'] = model.predict_class(month=str(pd.to_datetime(month).to_period('M')-1),
                                                 data=test)
            print(test[['M','M_pred']])
            break


def main():
    data = pd.read_csv('../data/preprocessed/data_for_convex.csv').drop('Unnamed: 0', axis=1)
    data.rename(columns={'RankID1':'RankID'},inplace=True)
    # test_checking_pipe(data)  #  check few months to see the class/ mean_rnpd making sense
    # test_loading_to_convex(data)  # check convex works
    # test_getting_model_scores(data)  #  check convex results scores
    # test_plot_all_months(data)  # plot all RNPD / Duration months for groups
    test_plot_all_months_animation(data)

if __name__ == '__main__':
    main()