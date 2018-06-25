import pandas as pd
import numpy as np
from copy import copy
from constants import MmxColumns, data_directory


def get_clean_data(df):
    df_clean = copy(df)
    loaded_valid_ids = []
    for station_id in df_clean.station_id.unique():
        try:
            raw = pd.read_csv(data_directory + '/Labels/Clean/' + str(station_id) + '_valid.csv', index_col=False,
                              header=None)
            loaded_valid_ids.append(raw)
        except FileNotFoundError:
            print('No clean data for station {0}. It will not be added into resulting dataframe'.format(station_id))

    valid_ids = pd.concat(loaded_valid_ids)
    valid_ids = list(valid_ids.values.ravel())
    df_clean['clean'] = df_clean[MmxColumns.ID_ROAD_TEMPERATURE].isin(valid_ids)
    df_clean = df_clean[df_clean['clean']]
    del df_clean['clean']
    return df_clean


def create_feature_df_one_station(df_pattern, target,
                                  winter_period=True,
                                  variables=(MmxColumns.ROAD_TEMPERATURE,
                                             MmxColumns.AIR_TEMPERATURE,
                                             MmxColumns.UNDERGROUND_TEMPERATURE,
                                             MmxColumns.PRESSURE,
                                             MmxColumns.HUMIDITY, ),
                                  interpol_freq=20,  # minutes
                                  lag_list=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10),
                                  diff_list=((1, 2), (2, 3), (3, 4), (4, 5), (5, 6)),
                                  coordinates=True, solar_angles=True, road_id=True,
                                  day_of_year=True, month=True, hour=True,
                                  post_process=True, regression_mode=True):
    df_res = pd.DataFrame(index=df_pattern.index)
    df_res[MmxColumns.DATE_TIME_UTC] = copy(df_pattern[MmxColumns.DATE_TIME_UTC])
    df_res[MmxColumns.STATION_ID] = copy(df_pattern[MmxColumns.STATION_ID])

    if 'label_true' in df_pattern.columns:
        df_res['label_true'] = df_pattern['label_true']

    # do not forget to change!!!! for any column
    if MmxColumns.ID_ROAD_TEMPERATURE in df_pattern.columns:
        df_res[MmxColumns.ID_ROAD_TEMPERATURE] = df_pattern[MmxColumns.ID_ROAD_TEMPERATURE]

    if winter_period:
        df_res = df_res[df_res[MmxColumns.DATE_TIME_UTC].dt.month.isin((1, 2, 3, 4, 5, 9, 10, 11, 12))]

    if coordinates:
        df_res[MmxColumns.LATITUDE] = copy(df_pattern[MmxColumns.LATITUDE])
        df_res[MmxColumns.LONGITUDE] = copy(df_pattern[MmxColumns.LONGITUDE])

    if solar_angles:
        df_res['data_solar_altitude'] = copy(df_pattern['data_solar_altitude'])
        df_res['data_solar_azimuth'] = copy(df_pattern['data_solar_azimuth'])

    if road_id:
        df_res['data_road'] = copy(df_pattern['data_road'])

    for column in variables:
        df_res[column] = copy(df_pattern[column])

        for lag in lag_list:
            lag_name = '{0}_lag_{1}'.format(column, lag * interpol_freq)
            # print(lag, lag_name)
            df_res[lag_name] = df_res[column].shift(int(lag))

        for diff in diff_list:
            diff_0 = interpol_freq * diff[0]
            diff_1 = interpol_freq * diff[1]
            diff_name = '{0}_diff_{1}_{2}'.format(column, diff_0, diff_1)
            # print(diff_name)
            df_res[diff_name] = df_res['{0}_lag_{1}'.format(column, diff_1)] \
                - df_res['{0}_lag_{1}'.format(column, diff_0)]

        if column != target:
            # print(0, column)
            if post_process:
                del df_res[column]

        else:
            # print(1, column)
            if regression_mode:
                target_column = 'target_{0}'.format('_'.join(column.split('_')[1:]))
                df_res[target_column] = df_res[column]
                del df_res[column]

    if day_of_year:
        # print('day_of_year')
        df_res['data_dayofyear_cos'] = np.cos(df_res['date_time_utc'].dt.dayofyear / 365 * np.pi)
        df_res['data_dayofyear_sin'] = np.sin(df_res['date_time_utc'].dt.dayofyear / 365 * np.pi)

    if month:
        # print('month')
        df_res['data_month_cos'] = np.cos(df_res['date_time_utc'].dt.month / 12 * np.pi)
        df_res['data_month_sin'] = np.sin(df_res['date_time_utc'].dt.month / 12 * np.pi)

    if hour:
        # print('hour')
        df_res['data_hour_cos'] = np.cos(df_res['date_time_utc'].dt.hour / 24 * np.pi)
        df_res['data_hour_sin'] = np.sin(df_res['date_time_utc'].dt.hour / 24 * np.pi)

    df_res = df_res.dropna()
    return df_res


def create_feature_df(df, target,
                      winter_period=True,
                      variables=(MmxColumns.ROAD_TEMPERATURE,
                                 MmxColumns.AIR_TEMPERATURE,
                                 MmxColumns.UNDERGROUND_TEMPERATURE,
                                 MmxColumns.PRESSURE,
                                 MmxColumns.HUMIDITY,),
                      interpol_freq=20,  # minutes
                      lag_list=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10),
                      diff_list=((1, 2), (2, 3), (3, 4), (4, 5), (5, 6)),
                      coordinates=True, solar_angles=True, road_id=True,
                      day_of_year=True, month=True, hour=True, post_process=True, regression_mode=True):

    df_res = df.groupby([MmxColumns.STATION_ID]). \
        apply(lambda x: create_feature_df_one_station(x, target,
                                                      winter_period, variables,
                                                      interpol_freq,
                                                      lag_list, diff_list,
                                                      coordinates, solar_angles,
                                                      road_id, day_of_year,
                                                      month, hour, post_process, regression_mode))
    df_res = df_res.reset_index(drop=True)
    return df_res
