import numpy as np
import pandas as pd
from constants import RP5Columns, MmxColumns, MmccRwisColumns, MmccForecastColumns, \
    MmxPrecipitationCode, data_directory
from date_time_handlers import add_utc, rp5_datetime_to_mmx_format, mmx_datetime_to_mmcc_format

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
    "Метель": MmxPrecipitationCode.SNOW
}

map_p_weather_rp5_to_mmx = {
    np.nan: 0,
    "Облака покрывали более половины неба в течение всего соответствующего периода.": 0,
    "Облака покрывали более половины неба в течение одной части соответствующего периода" +
    " и половину или менее в течение другой части периода.": 0,
    "Облака покрывали половину неба или менее в течение всего соответствующего периода.": 0,
    "Туман или ледяной туман или сильная мгла.": 20,
    "Никаких особых явлений погоды не наблюдалось.": 0,
    "Буря": 30,

    "Гроза (грозы) с осадками или без них.": 40,
    "Морось.": 0,
    "Дождь.": 0,
    "Ливень (ливни).": 0,
    "Снег и/или другие виды твердых осадков": 0,
    "Дождь со снегом или другими видами твердых осадков": 0,
    "Метель": 40
}

map_precip_count_rp5_to_mmx = {
    "Осадков нет": 0,
    "Следы осадков": 0.05
}

map_visibility_rp5_to_mmx = {
    "менее 0.05": 0.05,
    "менее 0.1": 0.1
}

map_data_rp5_to_mmx = {
    MmxColumns.STATION_ID: lambda df: df[RP5Columns.STATION_ID],
    MmxColumns.DATE_TIME_LOCAL: lambda df: pd.to_datetime(df[RP5Columns.DATE_TIME_LOCAL].
                                                          apply(rp5_datetime_to_mmx_format)),
    MmxColumns.AIR_TEMPERATURE: lambda df: df[RP5Columns.AIR_TEMPERATURE],
    MmxColumns.HUMIDITY: lambda df: df[RP5Columns.HUMIDITY],
    MmxColumns.WIND_SPEED: lambda df: df[RP5Columns.WIND_SPEED],
    MmxColumns.WIND_MAX_SPEED: lambda df: df[RP5Columns.WIND_MAX_SPEED],
    MmxColumns.WIND_DIRECTION: lambda df: df[RP5Columns.WIND_DIRECTION].replace(map_wind_dir_rp5_to_mmx),
    MmxColumns.PRECIPITATION_CODE: lambda df: pd.to_numeric(df[RP5Columns.PRECIPITATION_CODE].
                                                            replace(map_precip_code_rp5_to_mmx)),
    MmxColumns.PRECIPITATION_INTENSITY: lambda df: pd.to_numeric(df[RP5Columns.PRECIPITATION_INTENSITY].
                                                                 replace(map_precip_count_rp5_to_mmx)) /
    df[RP5Columns.PRECIPITATION_INTERVAL],

    MmxColumns.DEW_POINT: lambda df: df[RP5Columns.DEW_POINT],
    MmxColumns.PRESSURE: lambda df: df[RP5Columns.PRESSURE],
    MmxColumns.VISIBILITY: lambda df: 1000 * pd.to_numeric(df[RP5Columns.VISIBILITY].
                                                           replace(map_visibility_rp5_to_mmx)),

    MmxColumns.P_WEATHER: lambda df: df[RP5Columns.PRECIPITATION_CODE].replace(map_p_weather_rp5_to_mmx),
    MmxColumns.CLOUDINESS: lambda df: pd.to_numeric(df[RP5Columns.CLOUDINESS].
                                                    replace(map_cloudiness_rp5_to_mmx))
}

map_data_raw_to_mmx = {
    MmxColumns.STATION_ID: lambda df: df[MmxColumns.STATION_ID],
    MmxColumns.DATE_TIME_LOCAL: lambda df: df[MmxColumns.DATE_TIME_LOCAL],
    MmxColumns.DATE_TIME_UTC: lambda df: add_utc(df, data_directory + '/stations_mm94_def.csv'),
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
    MmxColumns.DEW_POINT: lambda df: df[MmxColumns.DEW_POINT] / 10,
    MmxColumns.SALINITY: lambda df: df[MmxColumns.SALINITY] / 10,
    MmxColumns.PRESSURE: lambda df: np.where((df[MmxColumns.PRESSURE] > 700) & (df[MmxColumns.PRESSURE] < 800),
                                             df[MmxColumns.PRESSURE] * 10, df[MmxColumns.PRESSURE]) / 10,
    MmxColumns.VISIBILITY: lambda df: df[MmxColumns.VISIBILITY] / 10,
    MmxColumns.P_WEATHER: lambda df: df[MmxColumns.P_WEATHER],
    MmxColumns.CLOUDINESS: lambda df: df[MmxColumns.CLOUDINESS] * 10,

    MmxColumns.ID_AIR_TEMPERATURE: lambda df: df[MmxColumns.ID_AIR_TEMPERATURE],
    MmxColumns.ID_ROAD_TEMPERATURE: lambda df: df[MmxColumns.ID_ROAD_TEMPERATURE],
    MmxColumns.ID_UNDERGROUND_TEMPERATURE: lambda df: df[MmxColumns.ID_UNDERGROUND_TEMPERATURE],
    MmxColumns.ID_HUMIDITY: lambda df: df[MmxColumns.ID_HUMIDITY],
    MmxColumns.ID_WIND_SPEED: lambda df: df[MmxColumns.ID_WIND_SPEED],
    MmxColumns.ID_WIND_MAX_SPEED: lambda df: df[MmxColumns.ID_WIND_MAX_SPEED],
    MmxColumns.ID_WIND_DIRECTION: lambda df: df[MmxColumns.ID_WIND_DIRECTION],
    MmxColumns.ID_PRECIPITATION_CODE: lambda df: df[MmxColumns.ID_PRECIPITATION_CODE],
    MmxColumns.ID_PRECIPITATION_INTENSITY: lambda df: df[MmxColumns.ID_PRECIPITATION_INTENSITY],
    MmxColumns.ID_FREEZING_POINT: lambda df: df[MmxColumns.ID_FREEZING_POINT],
    MmxColumns.ID_DEW_POINT: lambda df: df[MmxColumns.ID_DEW_POINT],
    MmxColumns.ID_SALINITY: lambda df: df[MmxColumns.ID_SALINITY],
    MmxColumns.ID_PRESSURE: lambda df: df[MmxColumns.ID_PRESSURE],
    MmxColumns.ID_VISIBILITY: lambda df: df[MmxColumns.ID_VISIBILITY],
    MmxColumns.ID_P_WEATHER: lambda df: df[MmxColumns.ID_P_WEATHER],
    MmxColumns.ID_CLOUDINESS: lambda df: df[MmxColumns.ID_CLOUDINESS]
}


map_data_mmx_to_mmcc_rwis = {
    MmccRwisColumns.STATION_ID: lambda df: df[MmxColumns.STATION_ID],
    MmccRwisColumns.DATE_TIME_UTC: lambda df: df[MmxColumns.DATE_TIME_UTC],
    MmccRwisColumns.DATE_TIME_METRO: lambda df: df[MmxColumns.DATE_TIME_UTC].apply(mmx_datetime_to_mmcc_format),
    MmccRwisColumns.AIR_TEMPERATURE: lambda df: df[MmxColumns.AIR_TEMPERATURE],
    MmccRwisColumns.ROAD_TEMPERATURE: lambda df: df[MmxColumns.ROAD_TEMPERATURE],
    MmccRwisColumns.UNDERGROUND_TEMPERATURE: lambda df: df[MmxColumns.UNDERGROUND_TEMPERATURE],
    MmccRwisColumns.HUMIDITY: lambda df: df[MmxColumns.HUMIDITY],
    MmccRwisColumns.WIND_SPEED: lambda df: df[MmxColumns.WIND_SPEED],
    MmccRwisColumns.WIND_MAX_SPEED: lambda df: df[MmxColumns.WIND_MAX_SPEED],
    MmccRwisColumns.WIND_DIRECTION: lambda df: df[MmxColumns.WIND_DIRECTION],
    MmccRwisColumns.PRECIPITATION_CODE: lambda df: df[MmxColumns.PRECIPITATION_CODE],
    MmccRwisColumns.PRECIPITATION_INTENSITY: lambda df: df[MmxColumns.PRECIPITATION_INTENSITY],
    MmccRwisColumns.FREEZING_POINT: lambda df: df[MmccRwisColumns.FREEZING_POINT],
    MmccRwisColumns.DEW_POINT: lambda df: df[MmxColumns.DEW_POINT],
    MmccRwisColumns.SALINITY: lambda df: df[MmxColumns.SALINITY],
    MmccRwisColumns.PRESSURE: lambda df: df[MmxColumns.PRESSURE]
}

map_data_mmx_to_mmcc_forecast = {
    MmccForecastColumns.STATION_ID: lambda df: df[MmxColumns.STATION_ID],
    MmccForecastColumns.DATE_TIME_UTC: lambda df: df[MmxColumns.DATE_TIME_UTC],
    MmccForecastColumns.DATE_TIME_METRO: lambda df: df[MmxColumns.DATE_TIME_UTC].apply(mmx_datetime_to_mmcc_format),
    MmccForecastColumns.AIR_TEMPERATURE: lambda df: df[MmxColumns.AIR_TEMPERATURE].round(1),
    MmccForecastColumns.HUMIDITY: lambda df: df[MmxColumns.HUMIDITY].round(1),
    MmccForecastColumns.WIND_SPEED: lambda df: df[MmxColumns.WIND_SPEED].round(1),
    MmccForecastColumns.WIND_DIRECTION: lambda df: df[MmxColumns.WIND_DIRECTION].round(1),
    MmccForecastColumns.PRECIPITATION_CODE: lambda df: df[MmxColumns.PRECIPITATION_CODE].round(1),
    MmccForecastColumns.PRECIPITATION_INTENSITY: lambda df: df[MmxColumns.PRECIPITATION_INTENSITY].round(1),
    MmccForecastColumns.DEW_POINT: lambda df: df[MmxColumns.DEW_POINT].round(1),
    MmccForecastColumns.PRESSURE: lambda df: df[MmxColumns.PRESSURE].round(1),
    MmccForecastColumns.VISIBILITY: lambda df: df[MmxColumns.VISIBILITY].round(1),
    MmccForecastColumns.P_WEATHER: lambda df: df[MmxColumns.P_WEATHER].round(-1),
    MmccForecastColumns.CLOUDINESS: lambda df: df[MmxColumns.CLOUDINESS].round(-1)
}
