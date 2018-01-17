import numpy as np
import pandas as pd

FORECAST_HOURS_BEFORE_PREDICTION = 3
FORECAST_HOURS_AFTER_PREDICTION = 48

RUSSIAN_TIME_ZONES = {
    2: 'USZ1',
    3: 'MSK',
    4: 'SAMT',
    8: 'IRKT',
    5: 'YEKT',
    6: 'OMSK',
    7: 'KRAT',
    9: 'YAKT',
    10: 'VLAT',
    11: 'MAGT',
    12: 'PETT'
}

class RP5Columns:
    AIR_TEMPERATURE = 'T'
    HUMIDITY = 'U'
    WIND_SPEED = 'Ff'
    WIND_MAX_SPEED = 'ff10'
    WIND_DIRECTION = 'DD'
    PRECIPITATION_CODE = 'W1'
    PRECIPITATION_INTENSITY = 'RRR'
    PRECIPITATION_INTERVAL = 'tR'
    DEW_POINT_TEMPERATURE = 'Td'
    PRESSURE = 'P'
    VISIBILITY = 'VV'
    P_WEATHER = 'WW'
    CLOUDINESS = 'N'
    STATION_ID = 'station_id'
    DATE_TIME_LOCAL = 'Местное время'


class RawColumns:
    """
    Abbreviations from minimax system
    """
    AIR_TEMPERATURE = 't_air'
    ROAD_TEMPERATURE = 't_road'
    UNDERGROUND_TEMPERATURE = 't_underroad'
    HUMIDITY = 'dampness'
    WIND_SPEED = 'wind_velocity'
    WIND_MAX_SPEED = 'wind_speedmax'
    WIND_DIRECTION = 'wind_dir'
    PRECIPITATION_CODE = 'precip_code'
    PRECIPITATION_INTENSITY = 'precip_count'
    PRECIPITATION_INTERVAL = 'precip_interval'
    FREEZING_POINT = 'freezing_point'
    DEW_POINT_TEMPERATURE = 'dew_point'
    SALINITY = 'salinity'
    PRESSURE = 'pressure'
    VISIBILITY = 'visibility'
    P_WEATHER = 'p_weather'
    CLOUDINESS = 'cloudiness'
    STATION_ID = 'station_id'
    DATE_TIME_LOCAL = 'date_time'
    DATE_TIME_UTC = 'date_time_utc'




class MmxColumns:
    """
    Abbreviations from minimax system
    """
    AIR_TEMPERATURE = 'data_t_air'
    ROAD_TEMPERATURE = 'data_t_road'
    UNDERGROUND_TEMPERATURE = 'data_t_underroad'
    HUMIDITY = 'data_dampness'
    WIND_SPEED = 'data_wind_velocity'
    WIND_MAX_SPEED = 'data_wind_speedmax'
    WIND_DIRECTION = 'data_wind_dir'
    PRECIPITATION_CODE = 'data_precip_code'
    PRECIPITATION_INTENSITY = 'data_precip_count'
    PRECIPITATION_INTERVAL = 'data_precip_interval'
    FREEZING_POINT = 'data_freezing_point'
    DEW_POINT_TEMPERATURE = 'data_dew_point'
    SALINITY = 'data_salinity'
    PRESSURE = 'data_pressure'
    VISIBILITY = 'data_visibility'
    P_WEATHER = 'data_p_weather'
    CLOUDINESS = 'data_cloudiness'
    STATION_ID = 'station_id'
    DATE_TIME_LOCAL = 'date_time'
    DATE_TIME_UTC = 'date_time_utc'
    ID_AIR_TEMPERATURE = 'id_t_air'
    ID_ROAD_TEMPERATURE = 'id_t_road'
    ID_UNDERGROUND_TEMPERATURE = 'id_t_underroad'
    ID_HUMIDITY = 'id_dampness'
    ID_WIND_SPEED = 'id_wind_velocity'
    ID_WIND_MAX_SPEED = 'id_wind_speedmax'
    ID_WIND_DIRECTION = 'id_wind_dir'
    ID_PRECIPITATION_CODE = 'id_precip_code'
    ID_PRECIPITATION_INTENSITY = 'id_precip_count'
    ID_PRECIPITATION_INTERVAL = 'id_precip_interval'
    ID_FREEZING_POINT = 'id_freezing_point'
    ID_DEW_POINT_TEMPERATURE = 'id_dew_point'
    ID_SALINITY = 'id_salinity'
    ID_PRESSURE = 'id_pressure'
    ID_VISIBILITY = 'id_visibility'
    ID_P_WEATHER = 'id_p_weather'
    ID_CLOUDINESS = 'id_cloudiness'

class MetroColumns:
    """
    Abbreviations from minimax system
    """
    AIR_TEMPERATURE = 't_air' #
    ROAD_TEMPERATURE = 't_road' #
    UNDERGROUND_TEMPERATURE = 't_underroad' #
    HUMIDITY = 'humidity' #
    WIND_SPEED = 'wind_speed' #
    WIND_MAX_SPEED = 'wind_gusts' #
    WIND_DIRECTION = 'wind_direction' #
    PRECIPITATION_CODE = 'precipitation_type' #
    PRECIPITATION_INTENSITY = 'precipitation_intensity' #
    FREEZING_POINT = 'freezing_point' #
    DEW_POINT_TEMPERATURE = 't_dew_point' #
    SALINITY = 'salinity' #
    PRESSURE = 'pressure' #
    VISIBILITY = 'visibility' #
    P_WEATHER = 'p_weather' #
    CLOUDINESS = 'cloudiness'

class MmxPrecipitationCode:
    """
    Naming MMX codes for precipitation
    """
    DRY = 0
    RAIN = 10
    SNOW = 20
    RAIN_AND_SNOW = 30
    HEAVY_SNOW = 40

field_converter_rp5_to_mmx = {
    RP5Columns.AIR_TEMPERATURE: MmxColumns.AIR_TEMPERATURE,
    RP5Columns.PRESSURE: MmxColumns.PRESSURE,
    RP5Columns.HUMIDITY: MmxColumns.HUMIDITY,
    RP5Columns.WIND_DIRECTION: MmxColumns.WIND_DIRECTION,
    RP5Columns.WIND_SPEED: MmxColumns.WIND_SPEED,
    RP5Columns.WIND_MAX_SPEED: MmxColumns.WIND_MAX_SPEED,
    RP5Columns.CLOUDINESS: MmxColumns.CLOUDINESS,
    RP5Columns.VISIBILITY: MmxColumns.VISIBILITY,
    RP5Columns.DEW_POINT_TEMPERATURE: MmxColumns.DEW_POINT_TEMPERATURE,
    RP5Columns.PRECIPITATION_INTENSITY: MmxColumns.PRECIPITATION_INTENSITY,  # quantity of precipitation (mm)
    RP5Columns.PRECIPITATION_INTERVAL: 'data_precip_interval',  # time interval during which precip_count was calculated
    RP5Columns.PRECIPITATION_CODE: MmxColumns.PRECIPITATION_CODE,
    RP5Columns.P_WEATHER: MmxColumns.P_WEATHER,
    RP5Columns.DATE_TIME_LOCAL: MmxColumns.DATE_TIME_LOCAL
}

field_converter_raw_to_mmx = {}

field_converter_mmx_to_metro = {
    MmxColumns.AIR_TEMPERATURE: MetroColumns.AIR_TEMPERATURE,
    MmxColumns.PRESSURE: MetroColumns.PRESSURE,
    MmxColumns.HUMIDITY: MetroColumns.HUMIDITY,
    MmxColumns.WIND_DIRECTION: MetroColumns.WIND_DIRECTION,
    MmxColumns.WIND_SPEED: MetroColumns.WIND_SPEED,
    MmxColumns.WIND_MAX_SPEED: MetroColumns.WIND_MAX_SPEED,
    MmxColumns.CLOUDINESS: MetroColumns.CLOUDINESS,
    MmxColumns.VISIBILITY: MetroColumns.VISIBILITY,
    MmxColumns.DEW_POINT_TEMPERATURE: MetroColumns.DEW_POINT_TEMPERATURE,
    MmxColumns.PRECIPITATION_INTENSITY: MetroColumns.PRECIPITATION_INTENSITY,  # quantity of precipitation (mm)
    MmxColumns.PRECIPITATION_CODE: MetroColumns.PRECIPITATION_CODE,
    MmxColumns.P_WEATHER: MetroColumns.P_WEATHER
}

converter_wind_dir_dict_rp5 = {
    "Штиль, безветрие": 0,
    "Ветер, дующий с юга": 0,
    "Ветер, дующий с юго-юго-запада": 22.5,
    "Ветер, дующий с юго-запада": 45,
    "Ветер, дующий с западо-юго-запада": 67.5,
    "Ветер, дующий с запада": 90,
    "Ветер, дующий с западо-северо-запада": 112.5,
    "Ветер, дующий с северо-запада": 135,
    "Ветер, дующий с северо-северо-запада": 157.5,
    "Ветер, дующий с севера": 180,
    "Ветер, дующий с северо-северо-востока": 202.5,
    "Ветер, дующий с северо-востока": 225,
    "Ветер, дующий с востоко-северо-востока": 247.5,
    "Ветер, дующий с востока": 270,
    "Ветер, дующий с востоко-юго-востока": 292.5,
    "Ветер, дующий с юго-востока": 315,
    "Ветер, дующий с юго-юго-востока": 337.5
}

converter_cloudiness_dict_rp5 = {
    "100%.": 100,
    "90  или более, но не 100%": 90,
    "70 – 80%.": 75,
    "60%.": 60,
    "50%.": 50,
    "40%.": 40,
    "20–30%.": 25,
    "10%  или менее, но не 0": 10,
    "Облаков нет.": 0,
    "Небо не видно из-за тумана и/или других метеорологических явлений.": np.nan
}

converter_precip_code_dict_rp5 = {
    np.nan: MmxPrecipitationCode.DRY,
    "Облака покрывали более половины неба в течение всего соответствующего периода.": MmxPrecipitationCode.DRY,
    "Облака покрывали более половины неба в течение одной части соответствующего периода" + \
    " и половину или менее в течение другой части периода.": MmxPrecipitationCode.DRY,
    "Облака покрывали половину неба или менее в течение всего соответствующего периода.": MmxPrecipitationCode.DRY,
    "Туман или ледяной туман или сильная мгла.": MmxPrecipitationCode.DRY,

    "Гроза (грозы) с осадками или без них.": MmxPrecipitationCode.RAIN,
    "Морось.": MmxPrecipitationCode.RAIN,
    "Дождь.": MmxPrecipitationCode.RAIN,
    "Ливень (ливни).": MmxPrecipitationCode.RAIN,
    "Снег и/или другие виды твердых осадков": MmxPrecipitationCode.SNOW,
    "Дождь со снегом или другими видами твердых осадков": MmxPrecipitationCode.RAIN_AND_SNOW,
    "Метель":  MmxPrecipitationCode.SNOW
}

converter_precip_count_dict_rp5 = {
    "Осадков нет": 0,
    "Следы осадков": 0.05
    }

converter_visibility_dict_rp5 = {
    "менее 0.05": 0.05,
    "менее 0.1": 0.1
}

def rp5_datetime_to_mmx_format(datetime_rp5):
    date, time = datetime_rp5.split(' ')
    date = '-'.join(date.split('.')[::-1])
    time = time + ':00'
    datetime_standard = date + ' ' + time
    return datetime_standard

def mmx_datetime_to_metro_format(date_time):
    return str(date_time).rsplit(":", maxsplit=1)[0] + ' UTC'

data_converter_rp5_to_mmx = {
    MmxColumns.WIND_DIRECTION: lambda df: df[MmxColumns.WIND_DIRECTION].replace(converter_wind_dir_dict_rp5),
    MmxColumns.CLOUDINESS: lambda df: df[MmxColumns.CLOUDINESS].replace(converter_cloudiness_dict_rp5),
    MmxColumns.PRECIPITATION_CODE: lambda df: df[MmxColumns.PRECIPITATION_CODE].replace(converter_precip_code_dict_rp5),
    MmxColumns.PRECIPITATION_INTENSITY:
        lambda df: pd.to_numeric(df[MmxColumns.PRECIPITATION_INTENSITY].replace(converter_precip_count_dict_rp5)) / \
                   df[MmxColumns.PRECIPITATION_INTERVAL],
    MmxColumns.VISIBILITY: lambda df: 1000 * pd.to_numeric(df[MmxColumns.VISIBILITY].replace(converter_visibility_dict_rp5)),
    MmxColumns.DATE_TIME_LOCAL: lambda df: pd.to_datetime(df[MmxColumns.DATE_TIME_LOCAL].apply(rp5_datetime_to_mmx_format))
}

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


