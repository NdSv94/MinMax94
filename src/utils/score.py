import pandas as pd
from constants import data_directory, MmxColumns


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


def calc_recall(df_test, station_list, window=pd.Timedelta('4h')):
    predicted_anomalies_ids = set()

    for station in station_list:
        df = df_test[df_test[MmxColumns.STATION_ID] == station]
        predicted_anomalies = df[df['label_predict'] == 1]
        for anomaly in predicted_anomalies.iterrows():
            dt = anomaly[1][MmxColumns.DATE_TIME_UTC]
            locality = df_test[(df_test[MmxColumns.DATE_TIME_UTC] >= (dt - window)) &
                               (df_test[MmxColumns.DATE_TIME_UTC] <= (dt + window))]

            predicted_anomalies_ids.update(set(locality.index))

    true_anomalies_ids = set(df_test[(df_test['label_true'] == 1) &
                                     (df_test[MmxColumns.STATION_ID].isin(station_list))].index)

    tp = set.intersection(true_anomalies_ids, predicted_anomalies_ids)
    recall = len(tp) / len(true_anomalies_ids)
    return recall


def calc_precision(df_test, station_list, window=pd.Timedelta('4h')):
    true_anomalies_ids = set()

    for station in station_list:
        df = df_test[df_test[MmxColumns.STATION_ID] == station]
        true_anomalies = df[df['label_true'] == 1]
        for anomaly in true_anomalies.iterrows():
            dt = anomaly[1][MmxColumns.DATE_TIME_UTC]
            locality = df_test[(df_test[MmxColumns.DATE_TIME_UTC] >= (dt - window)) &
                               (df_test[MmxColumns.DATE_TIME_UTC] <= (dt + window))]

            true_anomalies_ids.update(set(locality.index))

    predicted_anomalies_ids = set(df_test[((df_test['label_predict'] == 1) &
                                           (df_test[MmxColumns.STATION_ID].isin(station_list)))].index)

    tp = set.intersection(true_anomalies_ids, predicted_anomalies_ids)
    precision = len(tp) / len(predicted_anomalies_ids)
    return precision


def calc_f1_score(precision, recall):
    return 2 * precision * recall / (precision + recall)