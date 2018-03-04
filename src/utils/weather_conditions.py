from constants import MmxPrecipitationCode, MmxColumns
import numpy as np
import pandas as pd


def calc_rain_intensity(df_mmx):
    rain_mask = df_mmx[MmxColumns.PRECIPITATION_CODE] == MmxPrecipitationCode.RAIN
    rain_snow_mask = df_mmx[MmxColumns.PRECIPITATION_CODE] == MmxPrecipitationCode.RAIN_AND_SNOW
    data_rain_intensity = (rain_mask * df_mmx[MmxColumns.PRECIPITATION_INTENSITY] +
                           rain_snow_mask * df_mmx[MmxColumns.PRECIPITATION_INTENSITY] / 2)
    return data_rain_intensity


def calc_snow_intensity(df_mmx):
    snow_mask = df_mmx[MmxColumns.PRECIPITATION_CODE] == MmxPrecipitationCode.SNOW
    rain_snow_mask = df_mmx[MmxColumns.PRECIPITATION_CODE] == MmxPrecipitationCode.RAIN_AND_SNOW
    data_snow_intensity = (snow_mask * df_mmx[MmxColumns.PRECIPITATION_INTENSITY] +
                           rain_snow_mask * df_mmx[MmxColumns.PRECIPITATION_INTENSITY] / 2)
    return data_snow_intensity


def crossing_lines(dt, ts_1, ts_2):
    difference = ts_1 - ts_2

    state_line_crossing = np.sign(difference.shift(1)) != np.sign(difference)

    x = dt.astype(int)

    k_1 = (ts_1 - ts_1.shift(1)) / (x - x.shift(1))
    b_1 = (ts_1 * x.shift(1) - ts_1.shift(1) * x) / (x.shift(1) - x)

    k_2 = (ts_2 - ts_2.shift(1)) / (x - x.shift(1))
    b_2 = (ts_2 * x.shift(1) - ts_2.shift(1) * x) / (x.shift(1) - x)

    y_cross = (b_2 * k_1 - b_1 * k_2) / (k_1 - k_2)

    x_cross = (y_cross - b_1) / k_1
    x_cross = x_cross.replace([np.inf, -np.inf], np.nan) * state_line_crossing
    x_cross = x_cross * ((x.shift(1) <= x_cross) & (x_cross <= x))
    x_cross = x_cross.replace(0, np.nan)
    x_cross = pd.to_datetime(x_cross)

    return x_cross, y_cross


# Снег (без наката)
def is_loose_snow(df_mmx):
    state_t_road_below_zero = df_mmx[MmxColumns.ROAD_TEMPERATURE] < 0

    state_snow = calc_snow_intensity(df_mmx) > 0

    state_t_air_for_loose_snow = (((df_mmx[MmxColumns.AIR_TEMPERATURE] <= -6)
                                   & (-10 <= df_mmx[MmxColumns.AIR_TEMPERATURE])
                                   & (df_mmx[MmxColumns.HUMIDITY] <= 90))
                                  | (df_mmx[MmxColumns.AIR_TEMPERATURE] < -10))

    state_loose_snow = state_t_road_below_zero & state_snow & state_t_air_for_loose_snow

    return state_loose_snow


# Сильный снегопад (без наката)
def is_heavy_loose_snow(df_mmx):
    state_loose_snow = is_loose_snow(df_mmx)
    state_heavy_snow = calc_snow_intensity(df_mmx) >= 3
    return state_loose_snow & state_heavy_snow


# Слабый снегопад (без наката)
def is_light_loose_snow(df_mmx):
    state_loose_snow = is_loose_snow(df_mmx)
    state_light_snow = calc_snow_intensity(df_mmx) < 3
    return state_loose_snow & state_light_snow


# Снежный накат
def is_packed_snow(df_mmx):
    state_t_road_below_zero = df_mmx[MmxColumns.ROAD_TEMPERATURE] < 0
    state_snow = calc_snow_intensity(df_mmx) > 0

    state_t_air_for_packed_snow = ((df_mmx[MmxColumns.AIR_TEMPERATURE] > -6)
                                   | ((df_mmx[MmxColumns.AIR_TEMPERATURE] >= -10)
                                      & (df_mmx[MmxColumns.HUMIDITY] > 90)))

    state_packed_snow = state_t_road_below_zero & state_snow & state_t_air_for_packed_snow
    return state_packed_snow


# Гололед
def is_sleet(df_mmx):
    state_t_road_below_zero = df_mmx[MmxColumns.ROAD_TEMPERATURE] < 0
    state_rain = calc_rain_intensity(df_mmx) > 0
    state_sleet = state_t_road_below_zero & state_rain
    return state_sleet


# Гололедица
def is_ice_crusted_ground(df_mmx):
    state_no_sleet = ~is_sleet(df_mmx)

    snow_history_avg = calc_snow_intensity(df_mmx.set_index(MmxColumns.DATE_TIME_UTC)).rolling('4h').mean()
    state_snow_history = snow_history_avg > 0

    rain_history_avg = calc_rain_intensity(df_mmx.set_index(MmxColumns.DATE_TIME_UTC)).rolling('4h').mean()
    state_rain_history = rain_history_avg > 0

    road_history_avg = df_mmx.set_index(MmxColumns.DATE_TIME_UTC)[MmxColumns.ROAD_TEMPERATURE].rolling('4h').mean()
    state_t_road_history_above_zero = road_history_avg > 0

    state_ice_crusted_ground = (state_no_sleet & state_t_road_history_above_zero &
                                state_t_road_history_above_zero & (state_snow_history | state_rain_history))

    return state_ice_crusted_ground


# Конец образования инея
def is_frost_ending_point(df_mmx):
    state_no_snow = calc_snow_intensity(df_mmx) == 0
    state_no_rain = calc_rain_intensity(df_mmx) == 0
    state_t_road_below_zero = df_mmx[MmxColumns.ROAD_TEMPERATURE] < 0

    state_frost_ending_point = state_no_snow & state_no_rain & state_t_road_below_zero
    return state_frost_ending_point


# Начало образования инея
def is_frost_beginning_point(df_mmx):
    state_no_snow = calc_snow_intensity(df_mmx) == 0
    state_no_rain = calc_rain_intensity(df_mmx) == 0
    state_t_road_for_frost = df_mmx[MmxColumns.ROAD_TEMPERATURE] >= df_mmx[MmxColumns.DEW_POINT]
    state_frost_beginning_point = state_no_snow & state_no_rain & state_t_road_for_frost
    return state_frost_beginning_point


# Средняя точка образования инея
def is_frost_middle_point(df_mmx):
    x_cross, y_cross = crossing_lines(df_mmx[MmxColumns.DATE_TIME_LOCAL],
                                      df_mmx[MmxColumns.ROAD_TEMPERATURE],
                                      df_mmx[MmxColumns.DEW_POINT])

    state_frost_middle_point = x_cross.notnull() & (y_cross < 0)
    return state_frost_middle_point


# Иней
def is_frost(df_mmx):
    state_frost_middle_point = is_frost_middle_point(df_mmx)
    state_frost_beginning_point = is_frost_beginning_point(df_mmx)
    state_frost_ending_point = is_frost_ending_point(df_mmx)

    df = pd.concat((df_mmx[MmxColumns.DATE_TIME_UTC], state_frost_beginning_point,
                    state_frost_middle_point, state_frost_ending_point), axis=1)
    df = df.rename(columns={0: 'start', 1: 'middle', 2: 'end'})
    df = df.set_index(MmxColumns.DATE_TIME_UTC)
    df['state_frost'] = False

    for row in df.iterrows():
        dt = row[0]
        window = df[(df.index <= dt) & (df.index >= (dt - pd.Timedelta('1h')))]
        if window.loc[window.index.max()]['end']:
            if window.start.sum() > 0:
                if window.middle.sum() > 0:
                    if window[window.middle].index.max() >= window[window.start].index.min():
                        df['state_frost'][df.index == dt] = True

    df = df.reset_index()
    state_frost = df['state_frost']
    return state_frost
