import numpy as np
import pandas as pd
import geopy.distance
from copy import deepcopy


def vincenty_dist(point_1, point_2):
    """point = tuple(lat, long)"""
    return geopy.distance.vincenty(point_1, point_2).km
#--------------------------------------------------------------------------

class Preprocessor():

    def __init__(self):
        pass


    def CreatePatternList(self, df_pivoted, max_gap=pd.Timedelta('2h'), min_length=pd.Timedelta('12h')):
        pattern_list = [g for _, g in df_pivoted.groupby([MmxColumns.STATION_ID, (df_pivoted.date_time_utc.diff() > max_gap).cumsum()])
                            if g.date_time_utc.iloc[-1] - g.date_time_utc.iloc[0] > min_length]
        df_patterns = pd.concat(pattern_list)
        return df_patterns

    
    def InterpolatePatterns(self, df_patterns):

        id_columns = [column for column in df_patterns.columns if column.startswith('id_')]
        data_columns = [column for column in df_patterns.columns if column.startswith('data_')]

        data_integer_columns = [column for column in data_columns if column
                                in (MmxColumns.PRECIPITATION_CODE, )]
        data_continuous_columns = [column for column in data_columns if column not in data_integer_columns]

        def interpolate(df):

            df_result = deepcopy(df)
            df_result = df_result.set_index(MmxColumns.DATE_TIME_UTC)
            df_result['interpol'] = False

            # create table with rounded date_time
            start = df_result.index.min().round('1h')
            end = df_result.index.max().round('1h')

            start_loc = df_result.date_time.min().round('1h')
            end_loc = df_result.date_time.max().round('1h')

            df_add = pd.DataFrame(index=pd.date_range(start, end, freq='1h', name=MmxColumns.DATE_TIME_UTC))
            df_add['interpol'] = True
            df_add[MmxColumns.DATE_TIME_LOCAL] = pd.date_range(start_loc, end_loc, freq='1h', name=MmxColumns.DATE_TIME_LOCAL)
            df_add[MmxColumns.STATION_ID] = df_result[MmxColumns.STATION_ID].unique()[0]

            df_result = df_result.merge(df_add, how='outer', on=[MmxColumns.STATION_ID, 'interpol', MmxColumns.DATE_TIME_LOCAL], left_index=True,
                                        right_index=True, sort=True)

            for column in data_continuous_columns:
                df_result[column] = df_result[column].interpolate(method='linear', limit_directiom='both', limit=6)

            for column in data_integer_columns:
                if column == MmxColumns.PRECIPITATION_CODE:
                    df_result[column] = df_result[column].interpolate(method='nearest', limit_directiom='both', limit=6)


            for column in id_columns:
                df_result[column] = df_result[column].interpolate(method='nearest', limit_direction='both', limit=6)

            df_result = df_result[df_result['interpol']]
            del df_result['interpol']
            df_result = df_result.dropna(thresh=3, subset=data_columns)
            df_result = df_result.reset_index()
            return df_result

        df_interpolated = df_patterns.groupby([pd.Grouper(MmxColumns.STATION_ID)]).apply(interpolate).reset_index(level=MmxColumns.STATION_ID, drop=True)
        return df_interpolated
