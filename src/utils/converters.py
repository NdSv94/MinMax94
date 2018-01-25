import pandas as pd
import numpy as np
from copy import copy
from constants import map_visibility_rp5_to_mmx, map_precip_count_rp5_to_mmx, \
    map_precip_code_rp5_to_mmx, map_cloudiness_rp5_to_mmx, \
    map_wind_dir_rp5_to_mmx, mmx_meteo_columns, MmxColumns, RP5Columns, RawColumns, mmcc_rwis_meteo_columns, \
    MmccRwisColumns, MmccForecastColumns, mmcc_forecast_meteo_columns, map_p_weather_rp5_to_mmx, data_directory


def rp5_datetime_to_mmx_format(datetime_rp5):
    date, time = datetime_rp5.split(' ')
    date = '-'.join(date.split('.')[::-1])
    time = time + ':00'
    datetime_standard = date + ' ' + time
    return datetime_standard


def mmx_datetime_to_mmcc_format(date_time):
    return str(date_time).rsplit(":", maxsplit=1)[0] + ' UTC'


def add_utc(df_raw, station_def_path=data_directory + '/stations_mm94_def.csv'):
    df_todo = copy(df_raw)
    station_def = pd.read_csv(station_def_path)

    def utc_time(df, station_id):
        timezone = station_def['timezone'][station_def[MmxColumns.STATION_ID] == station_id].values[0]
        df[MmxColumns.DATE_TIME_UTC] = pd.to_datetime(
            df[MmxColumns.DATE_TIME_LOCAL] - pd.Timedelta(str(timezone) + 'h'))
        return df

    date_time_utc = df_todo.groupby(MmxColumns.STATION_ID).apply(
        lambda df: utc_time(df, df.name)[[MmxColumns.DATE_TIME_UTC]])
    return date_time_utc

def set_onelevel(df):
    df_return = copy(df)
    df_return.columns = ['_'.join(col).strip()
                         if col not in ((MmxColumns.DATE_TIME_UTC, ''), (MmxColumns.STATION_ID, ''),
                                        (MmxColumns.DATE_TIME_LOCAL, ''))
                         else ''.join(col).strip() for col in df.columns.values]
    return df_return


def pivot_table(df):
    upper_columns = [col for col in df.columns if col in ('data', 'id', 'valid')]
    df_pivoted = df.pivot_table(index=[MmxColumns.STATION_ID, MmxColumns.DATE_TIME_LOCAL], columns='type', values=upper_columns)
    df_pivoted = df_pivoted.reset_index()
    df_pivoted.columns.names = [None] * len(df_pivoted.columns.names)
    df_pivoted = set_onelevel(df_pivoted)
    return df_pivoted

def convert_rp5_to_mmx(df_rp5):
    df = copy(df_rp5)

    columns_to_use = copy(mmx_meteo_columns)
    columns_to_use.remove(MmxColumns.ROAD_TEMPERATURE)
    columns_to_use.remove(MmxColumns.UNDERGROUND_TEMPERATURE)
    columns_to_use.remove(MmxColumns.SALINITY)

    df_mmx = pd.DataFrame(index=df.index, columns=columns_to_use)

    df_mmx[MmxColumns.STATION_ID] = df[RP5Columns.STATION_ID]
    df_mmx[MmxColumns.DATE_TIME_LOCAL] = pd.to_datetime(df[RP5Columns.DATE_TIME_LOCAL].
                                                        apply(rp5_datetime_to_mmx_format))
    df_mmx[MmxColumns.DATE_TIME_UTC] = add_utc(df_mmx, data_directory + '/stations_rp5_def.csv')
    df_mmx[MmxColumns.AIR_TEMPERATURE] = df[RP5Columns.AIR_TEMPERATURE]
    df_mmx[MmxColumns.HUMIDITY] = df[RP5Columns.HUMIDITY]
    df_mmx[MmxColumns.WIND_SPEED] = df[RP5Columns.WIND_SPEED]
    df_mmx[MmxColumns.WIND_MAX_SPEED] = df[RP5Columns.WIND_MAX_SPEED]
    df_mmx[MmxColumns.WIND_DIRECTION] = df[RP5Columns.WIND_DIRECTION].replace(map_wind_dir_rp5_to_mmx)

    df_mmx[MmxColumns.PRECIPITATION_CODE] = pd.to_numeric(df[RP5Columns.PRECIPITATION_CODE].
                                                          replace(map_precip_code_rp5_to_mmx))

    df_mmx[MmxColumns.PRECIPITATION_INTENSITY] = pd.to_numeric(df[RP5Columns.PRECIPITATION_INTENSITY].
                                                               replace(map_precip_count_rp5_to_mmx)) / \
        df[RP5Columns.PRECIPITATION_INTERVAL]

    df_mmx[MmxColumns.DEW_POINT] = df[RP5Columns.DEW_POINT]
    df_mmx[MmxColumns.PRESSURE] = df[RP5Columns.PRESSURE]
    df_mmx[MmxColumns.VISIBILITY] = 1000 * pd.to_numeric(df[RP5Columns.VISIBILITY].
                                                         replace(map_visibility_rp5_to_mmx))
    # TODO: code a parser for p_weather parameter
    df_mmx[MmxColumns.P_WEATHER] = df[RP5Columns.PRECIPITATION_CODE].replace(map_p_weather_rp5_to_mmx)

    df_mmx[MmxColumns.CLOUDINESS] = pd.to_numeric(df[RP5Columns.CLOUDINESS].
                                                  replace(map_cloudiness_rp5_to_mmx))
    df_mmx = df_mmx.sort_values(MmxColumns.DATE_TIME_UTC)
    return df_mmx


def convert_raw_to_mmx(df_raw):
    df = copy(df_raw)
    df = pivot_table(df)
    df_mmx = pd.DataFrame(index=df.index, columns=mmx_meteo_columns)
    print(mmx_meteo_columns)

    df_mmx[MmxColumns.STATION_ID] = df[RawColumns.STATION_ID]
    df_mmx[MmxColumns.DATE_TIME_LOCAL] = df[RawColumns.DATE_TIME_LOCAL]
    df_mmx[MmxColumns.DATE_TIME_UTC] = add_utc(df_mmx, data_directory + '/stations_mm94_def.csv')
    df_mmx[MmxColumns.AIR_TEMPERATURE] = df[RawColumns.AIR_TEMPERATURE] / 10
    df_mmx[MmxColumns.ROAD_TEMPERATURE] = df[RawColumns.ROAD_TEMPERATURE] / 10
    df_mmx[MmxColumns.UNDERGROUND_TEMPERATURE] = df[RawColumns.UNDERGROUND_TEMPERATURE] / 10
    df_mmx[MmxColumns.HUMIDITY] = df[RawColumns.HUMIDITY] / 10
    df_mmx[MmxColumns.WIND_SPEED] = df[RawColumns.WIND_SPEED] / 10
    df_mmx[MmxColumns.WIND_MAX_SPEED] = df[RawColumns.WIND_MAX_SPEED] / 10
    df_mmx[MmxColumns.WIND_DIRECTION] = df[RawColumns.WIND_DIRECTION] * 45
    df_mmx[MmxColumns.PRECIPITATION_CODE] = df[RawColumns.PRECIPITATION_CODE] * 10
    df_mmx[MmxColumns.PRECIPITATION_INTENSITY] = df[RawColumns.PRECIPITATION_INTENSITY] / 10
    df_mmx[MmxColumns.FREEZING_POINT] = df[RawColumns.FREEZING_POINT] / 10
    df_mmx[MmxColumns.DEW_POINT] = df[RawColumns.DEW_POINT] / 10
    df_mmx[MmxColumns.SALINITY] = df[RawColumns.SALINITY] / 10
    df_mmx[MmxColumns.PRESSURE] = np.where((df[MmxColumns.PRESSURE] > 700) & (df[MmxColumns.PRESSURE] < 800),
                                           df[MmxColumns.PRESSURE] * 10, df[MmxColumns.PRESSURE]) / 10
    #df_mmx[MmxColumns.VISIBILITY] = df[RawColumns.VISIBILITY] / 10
    #df_mmx[MmxColumns.P_WEATHER] = df[RawColumns.P_WEATHER]  # strange parameter, maybe set==0?
    df_mmx[MmxColumns.CLOUDINESS] = df[RawColumns.CLOUDINESS] * 10

    return df_mmx


def convert_mmx_to_mmcc_rwis(df_mmx):
    df = copy(df_mmx)
    df_rwis = pd.DataFrame(index=df.index, columns=mmcc_rwis_meteo_columns)

    df_rwis[MmccRwisColumns.STATION_ID] = df[MmxColumns.STATION_ID]
    df_rwis[MmccRwisColumns.DATE_TIME_UTC] = df_rwis[MmxColumns.DATE_TIME_UTC]
    df_rwis[MmccRwisColumns.DATE_TIME_METRO] = df_rwis[MmxColumns.DATE_TIME_UTC].apply(mmx_datetime_to_mmcc_format)
    df_rwis[MmccRwisColumns.AIR_TEMPERATURE] = df[MmxColumns.AIR_TEMPERATURE]
    df_rwis[MmccRwisColumns.ROAD_TEMPERATURE] = df[MmxColumns.ROAD_TEMPERATURE]
    df_rwis[MmccRwisColumns.UNDERGROUND_TEMPERATURE] = df[MmxColumns.UNDERGROUND_TEMPERATURE]
    df_rwis[MmccRwisColumns.HUMIDITY] = df[MmxColumns.HUMIDITY]
    df_rwis[MmccRwisColumns.WIND_SPEED] = df[MmxColumns.WIND_SPEED]
    df_rwis[MmccRwisColumns.WIND_MAX_SPEED] = df[MmxColumns.WIND_MAX_SPEED]
    df_rwis[MmccRwisColumns.WIND_DIRECTION] = df[MmxColumns.WIND_DIRECTION]
    df_rwis[MmccRwisColumns.PRECIPITATION_CODE] = df[MmxColumns.PRECIPITATION_CODE]
    df_rwis[MmccRwisColumns.PRECIPITATION_INTENSITY] = df[MmxColumns.PRECIPITATION_INTENSITY]
    df_rwis[MmccRwisColumns.FREEZING_POINT] = df[MmccRwisColumns.FREEZING_POINT]
    df_rwis[MmccRwisColumns.DEW_POINT_TEMPERATURE] = df[MmxColumns.DEW_POINT_TEMPERATURE]
    df_rwis[MmccRwisColumns.SALINITY] = df[MmxColumns.SALINITY]
    df_rwis[MmccRwisColumns.PRESSURE] = df[MmxColumns.PRESSURE]

    return df_rwis


def convert_mmx_to_mmcc_forecast(df_mmx):
    df = copy(df_mmx)
    df_forecast = pd.DataFrame(index=df.index, columns=mmcc_forecast_meteo_columns)

    df_forecast[MmccForecastColumns.STATION_ID] = df[MmxColumns.STATION_ID]
    df_forecast[MmccForecastColumns.DATE_TIME_UTC] = df[MmxColumns.DATE_TIME_UTC]
    df_forecast[MmccForecastColumns.DATE_TIME_METRO] = df[MmxColumns.DATE_TIME_UTC].apply(mmx_datetime_to_mmcc_format)
    df_forecast[MmccForecastColumns.AIR_TEMPERATURE] = df[MmxColumns.AIR_TEMPERATURE]
    df_forecast[MmccForecastColumns.HUMIDITY] = df[MmxColumns.HUMIDITY]
    df_forecast[MmccForecastColumns.WIND_SPEED] = df[MmxColumns.WIND_SPEED]
    df_forecast[MmccForecastColumns.WIND_DIRECTION] = df[MmxColumns.WIND_DIRECTION]
    df_forecast[MmccForecastColumns.PRECIPITATION_CODE] = df[MmxColumns.PRECIPITATION_CODE]
    df_forecast[MmccForecastColumns.PRECIPITATION_INTENSITY] = df[MmxColumns.PRECIPITATION_INTENSITY]
    df_forecast[MmccForecastColumns.DEW_POINT] = df[MmxColumns.DEW_POINT]
    df_forecast[MmccForecastColumns.PRESSURE] = df[MmxColumns.PRESSURE]
    df_forecast[MmccForecastColumns.VISIBILITY] = df[MmxColumns.VISIBILITY]
    df_forecast[MmccForecastColumns.P_WEATHER] = df[MmxColumns.P_WEATHER]
    df_forecast[MmccForecastColumns.CLOUDINESS] = df[MmxColumns.CLOUDINESS].round(-1)
    return df_forecast
