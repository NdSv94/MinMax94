import pandas as pd
from constants import data_directory, MmxColumns
from functools import reduce


def get_labels(df, labels_type='true'):
    valid_labels_type = {'true', 'generated'}
    if labels_type in valid_labels_type:
        if labels_type == 'generated':
            path = data_directory + '/Labels/Generated/'
        elif labels_type == 'true':
            path = data_directory + '/Labels/True/'
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


def get_points_locality(df, points_type, window=pd.Timedelta('2h')):
    valid_points_type = {'label_true', 'label_predict'}

    if points_type in valid_points_type:
        points_column = points_type
    else:
        raise ValueError("results: points_type must be one of %r." % valid_points_type)

    df_points = df[df[points_column] == 1]
    points_dt_list = list(df_points[MmxColumns.DATE_TIME_UTC])
    interval_list = [(tp - window, tp + window) for tp in points_dt_list]
    mask_list = [((df[MmxColumns.DATE_TIME_UTC] >= border[0]) & (df[MmxColumns.DATE_TIME_UTC] <= border[1])) for border
                 in interval_list]
    points_locality = reduce((lambda x, y: x | y), mask_list)
    return points_locality


def calculate_precision(df, window=pd.Timedelta('2h')):
    true_anomalies_locality = df.groupby(MmxColumns.STATION_ID).apply(
        lambda data: get_points_locality(data, 'label_true', window)).reset_index(drop=True)
    true_positive = df[true_anomalies_locality & (df['label_predict'] == 1)]
    predicted_anomalies = df[df['label_predict'] == 1]
    precision = len(true_positive) / len(predicted_anomalies)
    return precision


def calculate_recall(df, window=pd.Timedelta('2h')):
    predicted_anomalies_locality = df.groupby(MmxColumns.STATION_ID).apply(
        lambda data: get_points_locality(data, 'label_predict', window)).reset_index(drop=True)
    true_positive = df[predicted_anomalies_locality & (df['label_true'] == 1)]
    true_anomalies = df[df['label_true'] == 1]
    recall = len(true_positive) / len(true_anomalies)
    return recall
