import pandas as pd
# import numpy as np
from copy import copy
from date_time_handlers import add_utc
from constants import MmxColumns, data_directory, mmcc_rwis_columns, mmcc_forecast_columns, \
    mmx_basic_columns, mmx_columns
from map_data_dicts import map_data_rp5_to_mmx, map_data_raw_to_mmx, \
    map_data_mmx_to_mmcc_forecast, map_data_mmx_to_mmcc_rwis


def set_one_level(df):
    df_return = copy(df)
    df_return.columns = ['_'.join(col).strip()
                         if col not in ((MmxColumns.DATE_TIME_UTC, ''), (MmxColumns.STATION_ID, ''),
                                        (MmxColumns.DATE_TIME_LOCAL, ''))
                         else ''.join(col).strip() for col in df.columns.values]
    return df_return


def pivot_table(df):
    upper_columns = [col for col in df.columns if col in ('data', 'id', 'valid')]
    df_pivoted = df.pivot_table(index=[MmxColumns.STATION_ID, MmxColumns.DATE_TIME_LOCAL],
                                columns='type', values=upper_columns)
    df_pivoted = df_pivoted.reset_index()
    df_pivoted.columns.names = [None] * len(df_pivoted.columns.names)
    df_pivoted = set_one_level(df_pivoted)
    return df_pivoted


def convert_rp5_to_mmx(df_rp5, columns='all'):
    df = copy(df_rp5)
    df_mmx = pd.DataFrame(index=df.index)

    if columns == 'all':
        columns = mmx_columns

    elif columns == 'basic':
        columns = mmx_basic_columns

    for key, func in map_data_rp5_to_mmx.items():
        if key in columns:
            df_mmx[key] = func(df)

    df_mmx[MmxColumns.DATE_TIME_UTC] = add_utc(df_mmx, data_directory + '/stations_rp5_def.csv')
    df_mmx = df_mmx.sort_values(by=MmxColumns.DATE_TIME_UTC)
    return df_mmx


def convert_raw_to_mmx(df_raw, columns='all'):
    df = copy(df_raw)
    df = pivot_table(df)
    df_mmx = pd.DataFrame(index=df.index)

    if columns == 'all':
        columns = mmx_columns

    elif columns == 'basic':
        columns = mmx_basic_columns

    for key, func in map_data_raw_to_mmx.items():
        if key in columns:
            try:
                df_mmx[key] = func(df)
            except KeyError:
                # print('Column {} can not be calculated'.format(key))
                pass

    df_mmx = df_mmx.sort_values(by=MmxColumns.DATE_TIME_UTC)
    return df_mmx


def convert_mmx_to_mmcc_rwis(df_mmx):
    df = copy(df_mmx)
    df_rwis = pd.DataFrame(index=df.index, columns=mmcc_rwis_columns)

    for key, func in map_data_mmx_to_mmcc_rwis.items():
        try:
            df_rwis[key] = func(df)
        except KeyError:
            pass
            # print('Column {} can not be calculated'.format(key))

    df_rwis = df_rwis.fillna(9999)
    return df_rwis


def convert_mmx_to_mmcc_forecast(df_mmx):
    df = copy(df_mmx)
    df_forecast = pd.DataFrame(index=df.index, columns=mmcc_forecast_columns)

    for key, func in map_data_mmx_to_mmcc_forecast.items():
        try:
            df_forecast[key] = func(df)
        except KeyError:
            # print('Column {} can not be calculated'.format(key))
            pass

    df_forecast = df_forecast.fillna(9999)
    return df_forecast
