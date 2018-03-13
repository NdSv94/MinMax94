import pandas as pd
from constants import data_directory, MmxColumns
from copy import copy
import numpy as np


def get_labels(df, labels_type='true'):
    valid_labels_type = {'true', 'generated'}
    if labels_type in valid_labels_type:
        if labels_type == 'generated':
            path = data_directory + '/Labels/Generated/'
        elif labels_type == 'true':
            path = data_directory + '/Labels/Clean/'
    else:
        raise ValueError("results: labels_type must be one of %r." % valid_labels_type)

    loaded_valid_ids = []

    for station_id in df[MmxColumns.STATION_ID].unique():
        path_to_valid_labels = path + '{0}_valid.csv'.format(station_id)
        raw = pd.read_csv(path_to_valid_labels, index_col=False, header=None)
        loaded_valid_ids.append(raw)

    valid_ids = pd.concat(loaded_valid_ids)
    valid_ids = list(valid_ids.values.ravel())
    labels = (~df[MmxColumns.ID_ROAD_TEMPERATURE].isin(valid_ids)).astype(int)
    return labels


def calculate_status_one_station(y_true, y_predict, window_size=pd.Timedelta('2h')):

    # both y_true, y_predict -- timeseries with timestamp index

    true_positive = ((y_true.rolling(window_size).sum()) > 0).astype(int)
    predicted_positive = ((y_predict.rolling(window_size).sum()) > 0).astype(int)

    status = pd.Series(index=true_positive.index)

    status = np.where((true_positive & predicted_positive), 'tp', status)
    status = np.where((~true_positive & ~predicted_positive), 'tn', status)
    status = np.where((~true_positive & predicted_positive), 'fp', status)
    status = np.where((true_positive & ~predicted_positive), 'fn', status)
    return status


def calculate_status(df):
    columns_to_calc = ['date_time_utc', 'station_id', 'label_true', 'label_predict']
    df_status = copy(df[columns_to_calc].set_index('date_time_utc'))
    df_status['status'] = df_status.groupby('station_id').\
                            apply(lambda df: calculate_status_one_station(df['label_true'], 'label_predict'))
    df_status = df_status.reset_index(drop=False)
    return df_status
