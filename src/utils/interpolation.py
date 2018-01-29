import pandas as pd
from copy import deepcopy
from constants import MmxColumns, mmx_id_columns, mmx_basic_columns


continuous_mmx_columns = [MmxColumns.AIR_TEMPERATURE, MmxColumns.ROAD_TEMPERATURE, MmxColumns.UNDERGROUND_TEMPERATURE,
                          MmxColumns.HUMIDITY, MmxColumns.WIND_SPEED, MmxColumns.WIND_MAX_SPEED,
                          MmxColumns.WIND_DIRECTION, MmxColumns.PRECIPITATION_INTENSITY,
                          MmxColumns.FREEZING_POINT, MmxColumns.DEW_POINT, MmxColumns.SALINITY,
                          MmxColumns.PRESSURE, MmxColumns.VISIBILITY, MmxColumns.CLOUDINESS]

integer_mmx_columns = [MmxColumns.PRECIPITATION_CODE, MmxColumns.P_WEATHER] + mmx_id_columns


def create_patterns(df_mmx, max_gap=pd.Timedelta('2h'), min_length=pd.Timedelta('12h')):
    pattern_list = [g for _, g in
                    df_mmx.groupby([MmxColumns.STATION_ID, (df_mmx.date_time_utc.diff() > max_gap).cumsum()])
                    if g.date_time_utc.iloc[-1] - g.date_time_utc.iloc[0] > min_length]
    df_patterns = pd.concat(pattern_list)
    return df_patterns


def interpolate_mmx(df_mmx, freq_minutes=30):

    freq = pd.Timedelta(freq_minutes, unit="m")
    interpol_limit = round(180 / freq_minutes)

    data_integer_columns = [column for column in df_mmx.columns if column in integer_mmx_columns]
    data_continuous_columns = [column for column in df_mmx.columns if column in continuous_mmx_columns]

    def interpolate(df):

        df_result = deepcopy(df)
        df_result = df_result.set_index(MmxColumns.DATE_TIME_UTC)

        # create table with rounded date_time
        start = df_result.index.min().round(freq)
        end = df_result.index.max().round(freq)

        start_loc = df_result.date_time.min().round(freq)
        end_loc = df_result.date_time.max().round(freq)

        df_add = pd.DataFrame(index=pd.date_range(start, end, freq=freq, name=MmxColumns.DATE_TIME_UTC))
        df_add[MmxColumns.DATE_TIME_LOCAL] = pd.date_range(start_loc, end_loc, freq=freq,
                                                           name=MmxColumns.DATE_TIME_LOCAL)

        df_add[MmxColumns.STATION_ID] = df_result[MmxColumns.STATION_ID].unique()[0]

        df_result = df_result.merge(df_add, how='outer',
                                    on=[MmxColumns.STATION_ID, MmxColumns.DATE_TIME_LOCAL], left_index=True,
                                    right_index=True, sort=True)

        for column in data_continuous_columns:
            df_result[column] = df_result[column].\
                interpolate(method='linear', limit_directiom='both', limit=interpol_limit)

        for column in data_integer_columns:
            df_result[column] = df_result[column].\
                interpolate(method='nearest', limit_directiom='both', limit=interpol_limit)

        # choose only values in "round" timestamps
        mask = ((df_result.index.minute + df_result.index.hour * 60) % freq_minutes) == 0
        df_result = df_result[mask]
        df_result = df_result.dropna(thresh=3, subset=[col for col in mmx_basic_columns if col in df_result.columns])
        df_result = df_result.reset_index()
        return df_result

    df_mmx_interpolated = df_mmx.groupby([pd.Grouper(MmxColumns.STATION_ID)]).apply(interpolate).reset_index(
        level=MmxColumns.STATION_ID, drop=True)
    return df_mmx_interpolated
