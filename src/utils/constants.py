from abc import ABCMeta, abstractmethod

data_directory = "/mnt/HARD/MinMax94/data/CSV"

FORECAST_HOURS_BEFORE_PREDICTION = 3
FORECAST_HOURS_AFTER_PREDICTION = 48

available_meteo_parameters = ['t_air', 't_road', 't_underroad', 'dampness', 'wind_velocity', 'wind_speedmax',
                              'wind_dir', 'precip_code', 'precip_count', 'precip_interval', 'freezing_point',
                              'dew_point', 'salinity', 'pressure', 'visibility', 'p_weather', 'cloudiness']

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

ROAD_LAYERS = {
    "1": {"type": "asphalt", "thickness": 0.05},
    "2": {"type": "cement", "thickness": 0.25},
    "3": {"type": "crushed rock", "thickness": 0.20},
    "4": {"type": "sand", "thickness": 0.50}
}

ROAD_CATEGORY = 2

MAINTAINABILITY_LEVEL = 'high'


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
        return [attributes[key] for key in attributes.keys() if not
                key.startswith(('__', 'ID_', 'DATE_TIME', 'STATION_ID'))]

    @property
    def get_id_columns(self):
        attributes = self.__dict__
        return [attributes[key] for key in attributes.keys() if
                key.startswith('ID_')]


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
        self.DEW_POINT = 'Td'
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
        self.DATA = 'data'
        self.RECORD_ID = 'id'
        self.SENSOR_TYPE_ID = 'sensor_type_id'
        self.SENSOR_TYPE = 'type'
        self.SENSOR_ID = 'sensor_id'
        self.SENSOR_STATE = 'active_state'


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
        self.DEW_POINT = 'data_dew_point'
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
        self.ID_DEW_POINT = 'id_dew_point'
        self.ID_SALINITY = 'id_salinity'
        self.ID_PRESSURE = 'id_pressure'
        self.ID_VISIBILITY = 'id_visibility'
        self.ID_P_WEATHER = 'id_p_weather'
        self.ID_CLOUDINESS = 'id_cloudiness'


class MmccRwis(DataFrameColumns):
    """
    Abbreviations from Mmcc system
    """

    def __init__(self):
        super().__init__()
        self.STATION_ID = 'station_id'
        self.DATE_TIME_UTC = 'date_time_utc'
        self.DATE_TIME_METRO = 'date_time_metro'

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
        self.DEW_POINT = 't_dew_point'  #
        self.SALINITY = 'salinity'  #
        self.PRESSURE = 'pressure'  #


class MmccForecast(DataFrameColumns):
    """
    Abbreviations from mmcc system
    """

    def __init__(self):
        super().__init__()
        self.STATION_ID = 'station_id'
        self.DATE_TIME_UTC = 'date_time_utc'
        self.DATE_TIME_METRO = 'date_time_metro'

        self.AIR_TEMPERATURE = 't_air'  #
        self.HUMIDITY = 'humidity'  #
        self.WIND_SPEED = 'wind_speed'  #
        self.WIND_DIRECTION = 'wind_direction'  #
        self.PRECIPITATION_CODE = 'precipitation_type'  #
        self.PRECIPITATION_INTENSITY = 'precipitation_intensity'  #
        self.DEW_POINT = 't_dew_point'  #
        self.PRESSURE = 'pressure'  #
        self.VISIBILITY = 'visibility'  #
        self.P_WEATHER = 'p_weather'  #
        self.CLOUDINESS = 'cloudiness'  #


class MmxPrecipitationCode:
    """
    Naming MMX codes for precipitation
    """
    DRY = 0
    RAIN = 10
    SNOW = 20
    RAIN_AND_SNOW = 30
    HEAVY_SNOW = 40


RP5Columns = RP5()
RawColumns = Raw()
MmxColumns = Mmx()
MmccRwisColumns = MmccRwis()
MmccForecastColumns = MmccForecast()

rp5_columns = RP5Columns.get_columns
rp5_meteo_columns = RP5Columns.get_meteo_data_columns

raw_columns = RawColumns.get_columns
raw_meteo_columns = RawColumns.get_meteo_data_columns

mmx_columns = MmxColumns.get_columns
mmx_meteo_columns = MmxColumns.get_meteo_data_columns
mmx_id_columns = MmxColumns.get_id_columns
mmx_basic_columns = [MmxColumns.STATION_ID, MmxColumns.DATE_TIME_LOCAL, MmxColumns.DATE_TIME_UTC,
                     MmxColumns.AIR_TEMPERATURE, MmxColumns.ROAD_TEMPERATURE, MmxColumns.UNDERGROUND_TEMPERATURE,
                     MmxColumns.HUMIDITY, MmxColumns.PRESSURE]

mmcc_rwis_columns = MmccRwisColumns.get_columns
mmcc_rwis_meteo_columns = MmccRwisColumns.get_meteo_data_columns

mmcc_forecast_columns = MmccForecastColumns.get_columns
mmcc_forecast_meteo_columns = MmccForecastColumns.get_meteo_data_columns
