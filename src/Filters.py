import numpy as np
import pickle
import xgboost as xgb
from copy import deepcopy
from Preprocessing import set_onelevel, set_multilevel, UnLagTable
from matplotlib import pyplot as plt


def create_xgb_matrix(df, test_label):
    features = [col for col in df.columns.levels[0] if col.startswith('data_')]

    X_lag = np.arange(-6, 0, 0.5)
    add = [(col, 0) for col in features if (col != 'data_' + test_label)]

    X_label = [(feature, lag) for feature in features for lag in X_lag] + add
    y_label = [('data_' + test_label, 0)]

    X = df[X_label].values
    y = df[y_label].values.reshape(-1, 1)

    dxgb = xgb.DMatrix(X, y)

    return dxgb


#Quantile Regression objective. Smoothing is performed by Huber function
def quantile_huber_loss(preds, dtrain, _alpha, _delta):
    labels = dtrain.get_label()
    x = preds - labels
    loss = (x < (-_alpha * _delta)) * (-_alpha * x) + \
            ((x >= (-_alpha * _delta)) & (x < ((1. - _alpha) * _delta))) * (1. / (2 * _delta) * x ** 2) + \
            ((1. - _alpha) * x) * (x > ((1. - _alpha) * _delta))
    loss = np.sum(loss) / len(loss)
    return 'huber_quant', loss

#Grad and Hess of Huber quantile loss used for optimization in xgboost
def quantile_huber_obj(preds, dtrain, _alpha, _delta):
    labels = dtrain.get_label()
    x = preds - labels
    grad = (x < (-_alpha * _delta)) * (-_alpha) + \
            ((x >= (-_alpha * _delta)) & (x < ((1. - _alpha) * _delta))) * (1. / _delta * x) + \
            (1. - _alpha) * (x > ((1. - _alpha) * _delta))
    hess =  (1. / _delta) * ((x >= (-_alpha * _delta)) & (x < ((1. - _alpha) * _delta)))
    return grad, hess

#------------------------------------------------------------------------------------------------

class XGBFilter():
    def __init__(self, sensors=['t_road', 't_air', 't_underroad'], output='table',
                 path_to_filter='estimators/pima.pickle.'):
        self.sensors = sensors
        self.path = path_to_filter
        self.output = output

    def verify(self, df):
        invalid_ids = []
        if self.output == 'table':
            self.df_filtered = deepcopy(df)

        for test_label in self.sensors:

            dtest = create_xgb_matrix(df, test_label)

            # --------Upper/Lower---------
            model_upper = pickle.load(open(self.path + test_label + '_upper', 'rb'))
            model_lower = pickle.load(open(self.path + test_label + '_lower', 'rb'))

            y_upper = model_upper.predict(dtest).reshape(-1, 1)
            y_lower = model_lower.predict(dtest).reshape(-1, 1)
            y_true = dtest.get_label().reshape(-1, 1)

            if self.output == 'table':
                self.df_filtered[('valid_' + test_label, 0)] = ((y_true < y_upper) & (y_true > y_lower))
                self.verified = True

            elif self.output == 'ids':
                ids = df[('id_' + test_label, 0)][~df[('valid_' + test_label, 0)]].values
                invalid_ids.extend(ids)

        if self.output == 'table':
            return self.df_filtered
        elif self.output == 'ids':
            return invalid_ids

    def plot_filter_result(self, station, start='2012-01-01', end='2016-01-01', sensors=['t_road', 't_air']):
        df = UnLagTable(self.df_filtered)

        # selecting the exact station and time interval
        df_plot = df[df['station_id'] == station]
        df_plot = df_plot[(df_plot['date_time'] >= start) & (df_plot['date_time'] <= end)]

        color = ['b', 'g', 'm']
        i = 0
        plt.figure(figsize=(30, 10))
        for sensor in sensors:
            for elem in [True, False]:
                cond = df_plot[('valid', sensor)] == elem
                if elem:
                    plt.plot_date(df_plot[cond].date_time, df_plot[cond][('data', sensor)], color[i],
                                  linestyle='none', marker='o', label=sensor, markersize=6)

                else:
                    plt.plot_date(df_plot[cond].date_time, df_plot[cond][('data', sensor)], 'r.',
                                  linestyle='none', marker='o', label='_nolegend_', markersize=6)
            i += 1

        plt.title(sensor, fontsize=24)
        plt.legend(loc='upper right', fontsize=14)
        plt.grid(which='both')
        plt.show()
        pass