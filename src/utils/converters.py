import pandas as pd
import numpy as np
from copy import copy
from constants import rp5_meteo_columns, raw_meteo_columns, mmx_meteo_columns, mmcc_meteo_columns
from constants import map_visibility_rp5_to_mmx, map_precip_count_rp5_to_mmx, \
                    map_precip_code_rp5_to_mmx, map_cloudiness_rp5_to_mmx, \
                    map_wind_dir_rp5_to_mmx, mmx_meteo_columns, MmxColumns, RP5Columns, RawColumns


def rp5_datetime_to_mmx_format(datetime_rp5):
    date, time = datetime_rp5.split(' ')
    date = '-'.join(date.split('.')[::-1])
    time = time + ':00'
    datetime_standard = date + ' ' + time
    return datetime_standard


def mmx_datetime_to_metro_format(date_time):
    return str(date_time).rsplit(":", maxsplit=1)[0] + ' UTC'


def add_utc(df_raw, station_def_path='/mnt/HARD/MinMax94/data/data_all/CSV/stations_mm94_def.csv'):
    station_def = pd.read_csv(station_def_path)

    def utc_time(df, station_id):
        timezone = station_def['timezone'][station_def[MmxColumns.STATION_ID] == station_id].values[0]
        df[MmxColumns.DATE_TIME_UTC] = pd.to_datetime(
            df[MmxColumns.DATE_TIME_LOCAL] - pd.Timedelta(str(timezone) + 'h'))
        return df

    df_with_utc = df_raw.groupby(MmxColumns.STATION_ID).apply(lambda df: utc_time(df, df.name))
    return df_with_utc


def convert_rp5_to_mmx(df_rp5):
    df = copy(df_rp5)
    df_mmx = pd.DataFrame(index=df.index, columns=mmx_meteo_columns)

    # station_id column
    df_mmx[MmxColumns.STATION_ID] = df[RP5Columns.STATION_ID]

    # date_time column
    df_mmx[MmxColumns.DATE_TIME_LOCAL] = pd.to_datetime(df[RP5Columns.DATE_TIME_LOCAL].
                                                        apply(rp5_datetime_to_mmx_format))

    # wind_direction
    df_mmx[MmxColumns.WIND_DIRECTION] = df[RP5Columns.WIND_DIRECTION].replace(map_wind_dir_rp5_to_mmx)

    # precipitation code
    df_mmx[MmxColumns.PRECIPITATION_CODE] = pd.to_numeric(df[RP5Columns.PRECIPITATION_CODE].
                                                          replace(map_precip_code_rp5_to_mmx))

    # precipitation intensity
    df_mmx[MmxColumns.PRECIPITATION_INTENSITY] = pd.to_numeric(
        df[RP5Columns.PRECIPITATION_INTENSITY].replace(map_precip_count_rp5_to_mmx)) / df[RP5Columns.PRECIPITATION_INTERVAL]
    # visibility
    df_mmx[MmxColumns.VISIBILITY] = 1000 * pd.to_numeric(df[RP5Columns.VISIBILITY].
                                                         replace(map_visibility_rp5_to_mmx))

    # cloudiness
    df_mmx[MmxColumns.CLOUDINESS] = pd.to_numeric(df[RP5Columns.CLOUDINESS].
                                                  replace(map_cloudiness_rp5_to_mmx))
    # t_air
    df_mmx[MmxColumns.AIR_TEMPERATURE] = df[RP5Columns.AIR_TEMPERATURE]

    # humidity
    df_mmx[MmxColumns.HUMIDITY] = df[RP5Columns.HUMIDITY]

    # wind_speed
    df_mmx[MmxColumns.WIND_SPEED] = df[RP5Columns.WIND_SPEED]

    # maximum wind speed
    df_mmx[MmxColumns.WIND_MAX_SPEED] = df[RP5Columns.WIND_SPEED]

    # dew point temperature
    df_mmx[MmxColumns.DEW_POINT_TEMPERATURE] = df[RP5Columns.DEW_POINT_TEMPERATURE]

    # pressure
    df_mmx[MmxColumns.PRESSURE] = df[RP5Columns.PRESSURE]

    # p_weather
    df_mmx[MmxColumns.P_WEATHER] = df[RP5Columns.P_WEATHER]

    # adding utc_time
    df_mmx = add_utc(df_mmx, '/mnt/HARD/MinMax94/data/CSV/stations_mm94_def.csv')
    return df_mmx


def convert_raw_to_mmx(df_raw):
    df = copy(df_raw)
    df_mmx = pd.DataFrame(index=df.index, columns=mmx_meteo_columns)

    # station_id column
    df_mmx[MmxColumns.STATION_ID] = df[RawColumns.STATION_ID]

    # date_time column
    df_mmx[MmxColumns.DATE_TIME_LOCAL] = df[RawColumns.DATE_TIME_LOCAL]

    # wind_direction
    df_mmx[MmxColumns.WIND_DIRECTION] = df[RawColumns.WIND_DIRECTION].replace(map_wind_dir_rp5_to_mmx)

    # precipitation code
    df_mmx[MmxColumns.PRECIPITATION_CODE] = pd.to_numeric(df[RawColumns.PRECIPITATION_CODE].
                                                          replace(map_precip_code_rp5_to_mmx))

    # precipitation intensity
    df_mmx[MmxColumns.PRECIPITATION_INTENSITY] = pd.to_numeric(
        df[RP5Columns.PRECIPITATION_INTENSITY].replace(map_precip_count_rp5_to_mmx)) / \
                                                 df[RawColumns.PRECIPITATION_INTERVAL]
    # visibility
    df_mmx[MmxColumns.VISIBILITY] = 1000 * pd.to_numeric(df[RawColumns.VISIBILITY].
                                                         replace(map_visibility_rp5_to_mmx))

    # cloudiness
    df_mmx[MmxColumns.CLOUDINESS] = pd.to_numeric(df[RawColumns.CLOUDINESS].
                                                  replace(map_cloudiness_rp5_to_mmx))
    # t_air
    df_mmx[MmxColumns.AIR_TEMPERATURE] = df[RawColumns.AIR_TEMPERATURE]

    # humidity
    df_mmx[MmxColumns.HUMIDITY] = df[RawColumns.HUMIDITY]

    # wind_speed
    df_mmx[MmxColumns.WIND_SPEED] = df[RawColumns.WIND_SPEED]

    # maximum wind speed
    df_mmx[MmxColumns.WIND_MAX_SPEED] = df[RawColumns.WIND_MAX_SPEED]

    # dew point temperature
    df_mmx[MmxColumns.DEW_POINT_TEMPERATURE] = df[RawColumns.DEW_POINT_TEMPERATURE]

    # pressure
    df_mmx[MmxColumns.PRESSURE] = df[RawColumns.PRESSURE]

    # p_weather
    df_mmx[MmxColumns.P_WEATHER] = df[RawColumns.P_WEATHER]

    # adding utc_time
    df_mmx = add_utc(df_mmx, '/mnt/HARD/MinMax94/data/CSV/stations_rp5_def.csv')
    return df_mmx


"""
data_converter_raw_to_mmx = {
    MmxColumns.AIR_TEMPERATURE: lambda df: df[MmxColumns.AIR_TEMPERATURE] / 10,
    MmxColumns.ROAD_TEMPERATURE: lambda df: df[MmxColumns.ROAD_TEMPERATURE] / 10,
    MmxColumns.UNDERGROUND_TEMPERATURE: lambda df: df[MmxColumns.UNDERGROUND_TEMPERATURE] / 10,
    MmxColumns.HUMIDITY: lambda df: df[MmxColumns.HUMIDITY] / 10,
    MmxColumns.WIND_SPEED: lambda df: df[MmxColumns.WIND_SPEED] / 10,
    MmxColumns.WIND_MAX_SPEED: lambda df: df[MmxColumns.WIND_MAX_SPEED] / 10,
    MmxColumns.WIND_DIRECTION: lambda df: df[MmxColumns.WIND_DIRECTION] * 45,
    MmxColumns.PRECIPITATION_CODE: lambda df: df[MmxColumns.PRECIPITATION_CODE] * 10,
    MmxColumns.PRECIPITATION_INTENSITY: lambda df: df[MmxColumns.PRECIPITATION_INTENSITY] / 10,
    MmxColumns.FREEZING_POINT: lambda df: df[MmxColumns.FREEZING_POINT] / 10,
    MmxColumns.DEW_POINT_TEMPERATURE: lambda df: df[MmxColumns.DEW_POINT_TEMPERATURE] / 10,
    MmxColumns.SALINITY: lambda df: df[MmxColumns.SALINITY] / 10,
    MmxColumns.PRESSURE: lambda df:  np.where((df[MmxColumns.PRESSURE] > 700) & (df[(MmxColumns.PRESSURE)] < 800),
                                           df[(MmxColumns.PRESSURE)] * 10, df[(MmxColumns.PRESSURE)]) / 10,
    MmxColumns.VISIBILITY: lambda df: df[MmxColumns.VISIBILITY] / 10,
    MmxColumns.CLOUDINESS: lambda df: df[MmxColumns.CLOUDINESS] * 10,
}


data_converter_rp5_to_mmx = {
    MmxColumns.WIND_DIRECTION: lambda df: df[MmxColumns.WIND_DIRECTION].replace(converter_wind_dir_dict_rp5),
    MmxColumns.CLOUDINESS: lambda df: pd.to_numeric(df[MmxColumns.CLOUDINESS].replace(converter_cloudiness_dict_rp5)),
    MmxColumns.PRECIPITATION_CODE: lambda df: pd.to_numeric(df[MmxColumns.PRECIPITATION_CODE].replace(converter_precip_code_dict_rp5)),
    MmxColumns.PRECIPITATION_INTENSITY:
        lambda df: pd.to_numeric(df[MmxColumns.PRECIPITATION_INTENSITY].replace(converter_precip_count_dict_rp5)) / \
                   df[MmxColumns.PRECIPITATION_INTERVAL],
    MmxColumns.VISIBILITY: lambda df: 1000 * pd.to_numeric(df[MmxColumns.VISIBILITY].replace(converter_visibility_dict_rp5)),
    MmxColumns.DATE_TIME_LOCAL: lambda df: pd.to_datetime(df[MmxColumns.DATE_TIME_LOCAL].apply(rp5_datetime_to_mmx_format)),
}


data_converter_mmx_to_metro = {
    MetroColumns.AIR_TEMPERATURE: lambda df: df[MetroColumns.AIR_TEMPERATURE].round(1),
    MetroColumns.ROAD_TEMPERATURE: lambda df: df[MetroColumns.ROAD_TEMPERATURE].round(1),
    MetroColumns.UNDERGROUND_TEMPERATURE: lambda df: df[MetroColumns.UNDERGROUND_TEMPERATURE].round(1),
    MetroColumns.HUMIDITY: lambda df: df[MetroColumns.HUMIDITY].round(1),
    MetroColumns.WIND_SPEED: lambda df: df[MetroColumns.WIND_SPEED].round(1),
    MetroColumns.WIND_MAX_SPEED: lambda df: df[MetroColumns.WIND_MAX_SPEED].round(1),
    MetroColumns.WIND_DIRECTION: lambda df: df[MetroColumns.WIND_DIRECTION].round(1),
    MetroColumns.PRECIPITATION_CODE: lambda df: df[MetroColumns.PRECIPITATION_CODE],
    MetroColumns.PRECIPITATION_INTENSITY: lambda df: df[MetroColumns.PRECIPITATION_INTENSITY].round(1),
    MetroColumns.FREEZING_POINT: lambda df: df[MetroColumns.FREEZING_POINT].round(1),
    MetroColumns.DEW_POINT_TEMPERATURE: lambda df: df[MetroColumns.DEW_POINT_TEMPERATURE].round(1),
    MetroColumns.SALINITY: lambda df: df[MetroColumns.SALINITY].round(1),
    MetroColumns.PRESSURE: lambda df: df[MetroColumns.PRESSURE].round(1),
    MetroColumns.VISIBILITY: lambda df: df[MetroColumns.VISIBILITY].round(1),
    MetroColumns.P_WEATHER: lambda df: df[MetroColumns.P_WEATHER],
    MetroColumns.CLOUDINESS: lambda df: df[MetroColumns.CLOUDINESS].round(-1)
}"""
