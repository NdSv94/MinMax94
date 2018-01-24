import numpy as np
from abc import ABCMeta, abstractmethod

FORECAST_HOURS_BEFORE_PREDICTION = 3
FORECAST_HOURS_AFTER_PREDICTION = 48

available_meteo_parameters = ['t_air', 't_road', 't_underroad', 'dampness', 'wind_velocity', 'wind_speedmax',
                              'wind_dir', 'precip_code', 'precip_count', 'precip_interval', 'freezing_point',
                              'dew_point', 'salinity', 'pressure', 'visibility', 'p_weather', 'cloudiness']

RUSSIAN_TIME_ZONES = {
    2:  'USZ1',
    3:  'MSK',
    4:  'SAMT',
    8:  'IRKT',
    5:  'YEKT',
    6:  'OMSK',
    7:  'KRAT',
    9:  'YAKT',
    10: 'VLAT',
    11: 'MAGT',
    12: 'PETT'
}


class DataFrameColumns(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        pass

    @property
    def get_columns(self):
        attributes = self.__dict__
        return [attributes[key] for key in attributes.keys() if not key.startswith('__')]

    @property
    def get_meteo_data_columns(self):
        attributes = self.__dict__
        return [attributes[key] for key in attributes.keys() if not key.startswith(('__', 'ID_'))]


class RP5(DataFrameColumns):
    """
    Abbreviations from rp5.ru
    """
    def __init__(self):
        super().__init__()
        self.STATION_ID = 'station_id'
        self.DATE_TIME_LOCAL = 'Местное время'

        self.AIR_TEMPERATURE = 'T'
        self.HUMIDITY = 'U'
        self.WIND_SPEED = 'Ff'
        self.WIND_MAX_SPEED = 'ff10'
        self.WIND_DIRECTION = 'DD'
        self.PRECIPITATION_CODE = 'W1'
        self.PRECIPITATION_INTENSITY = 'RRR'
        self.PRECIPITATION_INTERVAL = 'tR'
        self.DEW_POINT_TEMPERATURE = 'Td'
        self.PRESSURE = 'P'
        self.VISIBILITY = 'VV'
        self.P_WEATHER = 'WW'
        self.CLOUDINESS = 'N'


class Raw(DataFrameColumns):
    """
    Abbreviations from minimax system
    """
    def __init__(self):
        super().__init__()
        self.STATION_ID = 'station_id'
        self.DATE_TIME_LOCAL = 'date_time'
        self.DATE_TIME_UTC = 'date_time_utc'

        self.AIR_TEMPERATURE = 'data_t_air'
        self.ROAD_TEMPERATURE = 'data_t_road'
        self.UNDERGROUND_TEMPERATURE = 'data_t_underroad'
        self.HUMIDITY = 'data_dampness'
        self.WIND_SPEED = 'data_wind_velocity'
        self.WIND_MAX_SPEED = 'data_wind_speedmax'
        self.WIND_DIRECTION = 'data_wind_dir'
        self.PRECIPITATION_CODE = 'data_precip_code'
        self.PRECIPITATION_INTENSITY = 'data_precip_count'
        self.FREEZING_POINT = 'data_freezing_point'
        self.DEW_POINT_TEMPERATURE = 'data_dew_point'
        self.SALINITY = 'data_salinity'
        self.PRESSURE = 'data_pressure'
        self.VISIBILITY = 'data_visibility'
        self.P_WEATHER = 'data_p_weather'
        self.CLOUDINESS = 'data_cloudiness'

        self.ID_AIR_TEMPERATURE = 'id_t_air'
        self.ID_ROAD_TEMPERATURE = 'id_t_road'
        self.ID_UNDERGROUND_TEMPERATURE = 'id_t_underroad'
        self.ID_HUMIDITY = 'id_dampness'
        self.ID_WIND_SPEED = 'id_wind_velocity'
        self.ID_WIND_MAX_SPEED = 'id_wind_speedmax'
        self.ID_WIND_DIRECTION = 'id_wind_dir'
        self.ID_PRECIPITATION_CODE = 'id_precip_code'
        self.ID_PRECIPITATION_INTENSITY = 'id_precip_count'
        self.ID_PRECIPITATION_INTERVAL = 'id_precip_interval'
        self.ID_FREEZING_POINT = 'id_freezing_point'
        self.ID_DEW_POINT_TEMPERATURE = 'id_dew_point'
        self.ID_SALINITY = 'id_salinity'
        self.ID_PRESSURE = 'id_pressure'
        self.ID_VISIBILITY = 'id_visibility'
        self.ID_P_WEATHER = 'id_p_weather'
        self.ID_CLOUDINESS = 'id_cloudiness'


class Mmx(DataFrameColumns):
    """
    Abbreviations from Skoltech system
    """
    def __init__(self):
        super().__init__()
        self.STATION_ID = 'station_id'
        self.DATE_TIME_LOCAL = 'date_time'
        self.DATE_TIME_UTC = 'date_time_utc'

        self.AIR_TEMPERATURE = 'data_t_air'
        self.ROAD_TEMPERATURE = 'data_t_road'
        self.UNDERGROUND_TEMPERATURE = 'data_t_underroad'
        self.HUMIDITY = 'data_dampness'
        self.WIND_SPEED = 'data_wind_velocity'
        self.WIND_MAX_SPEED = 'data_wind_speedmax'
        self.WIND_DIRECTION = 'data_wind_dir'
        self.PRECIPITATION_CODE = 'data_precip_code'
        self.PRECIPITATION_INTENSITY = 'data_precip_count'
        self.FREEZING_POINT = 'data_freezing_point'
        self.DEW_POINT_TEMPERATURE = 'data_dew_point'
        self.SALINITY = 'data_salinity'
        self.PRESSURE = 'data_pressure'
        self.VISIBILITY = 'data_visibility'
        self.P_WEATHER = 'data_p_weather'
        self.CLOUDINESS = 'data_cloudiness'

        self.ID_AIR_TEMPERATURE = 'id_t_air'
        self.ID_ROAD_TEMPERATURE = 'id_t_road'
        self.ID_UNDERGROUND_TEMPERATURE = 'id_t_underroad'
        self.ID_HUMIDITY = 'id_dampness'
        self.ID_WIND_SPEED = 'id_wind_velocity'
        self.ID_WIND_MAX_SPEED = 'id_wind_speedmax'
        self.ID_WIND_DIRECTION = 'id_wind_dir'
        self.ID_PRECIPITATION_CODE = 'id_precip_code'
        self.ID_PRECIPITATION_INTENSITY = 'id_precip_count'
        self.ID_PRECIPITATION_INTERVAL = 'id_precip_interval'
        self.ID_FREEZING_POINT = 'id_freezing_point'
        self.ID_DEW_POINT_TEMPERATURE = 'id_dew_point'
        self.ID_SALINITY = 'id_salinity'
        self.ID_PRESSURE = 'id_pressure'
        self.ID_VISIBILITY = 'id_visibility'
        self.ID_P_WEATHER = 'id_p_weather'
        self.ID_CLOUDINESS = 'id_cloudiness'


class MmccRwis(DataFrameColumns):
    """
    Abbreviations from mmcc system
    """
    def __init__(self):
        super().__init__()
        self.DATE_TIME_UTC = 'date_time_utc'
        self.DATE_TIME_METRO = 'date_time_metro'
        self.STATION_ID = 'station_id'

        self.AIR_TEMPERATURE = 't_air'  #
        self.ROAD_TEMPERATURE = 't_road'  #
        self.UNDERGROUND_TEMPERATURE = 't_underroad'  #
        self.HUMIDITY = 'humidity'  #
        self.WIND_SPEED = 'wind_speed'  #
        self.WIND_MAX_SPEED = 'wind_gusts'  #
        self.WIND_DIRECTION = 'wind_direction'  #
        self.PRECIPITATION_CODE = 'precipitation_type'  #
        self.PRECIPITATION_INTENSITY = 'precipitation_intensity'  #
        self.FREEZING_POINT = 'freezing_point'  #
        self.DEW_POINT_TEMPERATURE = 't_dew_point'  #
        self.SALINITY = 'salinity'  #
        self.PRESSURE = 'pressure'  #
        # VISIBILITY = 'visibility'
        # P_WEATHER = 'p_weather'
        # CLOUDINESS = 'cloudiness'


class MmccForecast(DataFrameColumns):
    """
    Abbreviations from mmcc system
    """
    def __init__(self):
        super().__init__()
        self.DATE_TIME_UTC = 'date_time_utc'
        self.DATE_TIME_METRO = 'date_time_metro'
        self.STATION_ID = 'station_id'

        self.AIR_TEMPERATURE = 't_air'  #
        self.HUMIDITY = 'humidity'  #
        self.WIND_SPEED = 'wind_speed'  #
        self.WIND_DIRECTION = 'wind_direction'  #
        self.PRECIPITATION_CODE = 'precipitation_type'  #
        self.PRECIPITATION_INTENSITY = 'precipitation_intensity'  #
        self.DEW_POINT_TEMPERATURE = 't_dew_point'  #
        self.PRESSURE = 'pressure'  #
        self.VISIBILITY = 'visibility'  #
        self.P_WEATHER = 'p_weather'  #
        self.CLOUDINESS = 'cloudiness'  #


RP5Columns = RP5()
RawColumns = Raw()
MmxColumns = Mmx()
MmccRwisColumns = MmccRwis()
MmccForecastColumns = MmccForecast()


rp5_meteo_columns = RP5Columns.get_meteo_data_columns
raw_meteo_columns = RawColumns.get_meteo_data_columns
mmx_meteo_columns = MmxColumns.get_meteo_data_columns
mmcc_rwis_meteo_columns = MmccRwisColumns.get_meteo_data_columns
mmcc_forecast_meteo_columns = MmccForecastColumns.get_meteo_data_columns

rp5_columns = RP5Columns.get_columns
raw_columns = RawColumns.get_columns
mmx_columns = MmxColumns.get_columns
mmcc_rwis_columns = MmccRwisColumns.get_columns
mmcc_forecast_columns = MmccForecastColumns.get_columns


class MmxPrecipitationCode:
    """
    Naming MMX codes for precipitation
    """
    DRY = 0
    RAIN = 10
    SNOW = 20
    RAIN_AND_SNOW = 30
    HEAVY_SNOW = 40


map_wind_dir_rp5_to_mmx = {
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


map_cloudiness_rp5_to_mmx = {
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


map_precip_code_rp5_to_mmx = {
    np.nan: MmxPrecipitationCode.DRY,
    "Облака покрывали более половины неба в течение всего соответствующего периода.": MmxPrecipitationCode.DRY,
    "Облака покрывали более половины неба в течение одной части соответствующего периода" +
    " и половину или менее в течение другой части периода.": MmxPrecipitationCode.DRY,
    "Облака покрывали половину неба или менее в течение всего соответствующего периода.": MmxPrecipitationCode.DRY,
    "Туман или ледяной туман или сильная мгла.": MmxPrecipitationCode.DRY,
    "Никаких особых явлений погоды не наблюдалось.": MmxPrecipitationCode.DRY,
    "Буря": MmxPrecipitationCode.DRY,

    "Гроза (грозы) с осадками или без них.": MmxPrecipitationCode.RAIN,
    "Морось.": MmxPrecipitationCode.RAIN,
    "Дождь.": MmxPrecipitationCode.RAIN,
    "Ливень (ливни).": MmxPrecipitationCode.RAIN,
    "Снег и/или другие виды твердых осадков": MmxPrecipitationCode.SNOW,
    "Дождь со снегом или другими видами твердых осадков": MmxPrecipitationCode.RAIN_AND_SNOW,
    "Метель":  MmxPrecipitationCode.SNOW
}


map_precip_count_rp5_to_mmx = {
    "Осадков нет": 0,
    "Следы осадков": 0.05
    }


map_visibility_rp5_to_mmx = {
    "менее 0.05": 0.05,
    "менее 0.1": 0.1
}
