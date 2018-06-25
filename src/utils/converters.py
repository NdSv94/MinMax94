import pandas as pd
import numpy as np
from copy import copy
from date_time_handlers import add_utc
from constants import MmxColumns, MmccRwisColumns, data_directory, mmcc_rwis_columns, mmcc_forecast_columns, \
    mmx_basic_columns, mmx_columns, mmx_meteo_columns
from map_data_dicts import map_data_rp5_to_mmx, map_data_raw_to_mmx, \
    map_data_mmx_to_mmcc_forecast, map_data_mmx_to_mmcc_rwis, map_data_mmcc_rwis_to_mmx
from interpolation import interpolate_mmx
from geographical import add_solar_angles


# --------------------------------------------------------------------------------
# Converters for training algorithms. Experimental stage
# --------------------------------------------------------------------------------
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
                # print(key)
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

    df_forecast['p_weather'] = df_forecast['p_weather'].fillna(0)
    df_forecast['wind_direction'] = df_forecast['wind_direction'].fillna(0)
    df_forecast['visibility'] = df_forecast['visibility'].fillna(10000)
    df_forecast['wind_speed'] = df_forecast['wind_speed'].fillna(2)
    df_forecast['humidity'] = df_forecast['humidity'].fillna(80)
    df_forecast['cloudiness'] = df_forecast['cloudiness'].fillna(70)
    df_forecast['precipitation_intensity'] = df_forecast['precipitation_intensity'].fillna(0)
    df_forecast['precipitation_type'] = df_forecast['precipitation_type'].fillna(0)
    df_forecast = df_forecast.fillna(9999)

    return df_forecast


def convert_mmcc_rwis_to_mmx(df_rwis):
    df = copy(df_rwis)
    df_mmx = pd.DataFrame(index=df.index, columns=mmx_meteo_columns)

    for key, func in map_data_mmcc_rwis_to_mmx.items():
        try:
            df_mmx[key] = func(df)
        except KeyError:
            pass

    df_mmx = df_mmx.replace({9999: np.nan})
    return df_mmx


# ---------------------------------------------------------------------------------------------
# Converters for application. Production stage
# ---------------------------------------------------------------------------------------------


def convert_input_for_anomaly_detection(input_json, interpol_freq=20):
    rwis_data = input_json['rwis_data']
    station_config = input_json['station_config']

    # Convert input json into pd.Dataframe of MmccRwis type
    rwis_df = pd.DataFrame.from_dict(rwis_data, orient='index', )
    rwis_df[MmccRwisColumns.DATE_TIME_METRO] = rwis_df.index
    rwis_df = rwis_df.reset_index(drop=True)
    rwis_df[MmccRwisColumns.STATION_ID] = station_config['station_id']

    # Convert MmccRwis table into Mmx table
    mmx_rwis = convert_mmcc_rwis_to_mmx(rwis_df)

    # Interpolate Mmx Table for further analysis
    mmx_rwis = interpolate_mmx(mmx_rwis, interpol_freq)

    # Adding geographical coordinates into Mmx table
    mmx_rwis[MmxColumns.LONGITUDE] = station_config['longitude']
    mmx_rwis[MmxColumns.LATITUDE] = station_config['latitude']

    # Adding solar angles into Mmx table
    mmx_rwis['data_solar_azimuth'], mmx_rwis['data_solar_altitude'] = add_solar_angles(mmx_rwis)
    return mmx_rwis
