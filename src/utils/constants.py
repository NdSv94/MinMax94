import numpy as np
import pandas as pd

FORECAST_HOURS_BEFORE_PREDICTION = 3
FORECAST_HOURS_AFTER_PREDICTION = 48

RUSSIAN_TIME_ZONES = {
    'USZ1': '2',
    'MSK': '3',
    'SAMT': '4',
    'IRKT': '8',
    'YEKT': '5',
    'OMSK': '6',
    'KRAT': '7',
    'YAKT': '9',
    'VLAT': '10',
    'MAGT': '11',
    'PETT': '12'
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

class MmxColumns:
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

class MmxPrecipitationCode:
    """
    Naming MMX codes for precipitation
    """
    DRY = 0
    RAIN = 10
    SNOW = 20
    RAIN_AND_SNOW = 30
    HEAVY_SNOW = 40

mapper_columns_rp5_to_mm94 = {
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
    RP5Columns.PRECIPITATION_INTERVAL: 'precip_interval',  # time interval during which precip_count was calculated
    RP5Columns.PRECIPITATION_CODE: MmxColumns.PRECIPITATION_CODE,
    RP5Columns.P_WEATHER: MmxColumns.P_WEATHER
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

    "Морось.": MmxPrecipitationCode.RAIN,
    "Дождь.": MmxPrecipitationCode.RAIN,
    "Ливень (ливни).": MmxPrecipitationCode.RAIN,
    "Снег и/или другие виды твердых осадков": MmxPrecipitationCode.SNOW,
    "Дождь со снегом или другими видами твердых осадков": MmxPrecipitationCode.RAIN_AND_SNOW,
    "Метель":  MmxPrecipitationCode.SNOW
}

converter_precip_count_dict_rp5 = {
    np.nan:    np.nan,
    "Осадков нет": 0,
    "Следы осадков": 0.05
    }

mapper_converter_to_column = {
    MmxColumns.WIND_DIRECTION: lambda column: column.replace(converter_wind_dir_dict_rp5),
    MmxColumns.CLOUDINESS: lambda column: column.replace(converter_cloudiness_dict_rp5),
    MmxColumns.PRECIPITATION_CODE: lambda column: column.replace(converter_precip_code_dict_rp5),
    MmxColumns.PRECIPITATION_INTENSITY: lambda column: pd.to_numeric(column.replace(converter_precip_count_dict_rp5)),
    MmxColumns.VISIBILITY: lambda column: column * 1000
}

