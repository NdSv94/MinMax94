import numpy as np
import pandas as pd
from copy import deepcopy
from constants import MmxColumns
from constants import mapper_converter_to_mm94_column

def set_onelevel(df):
    df_return = deepcopy(df)
    df_return.columns = ['_'.join(col).strip() if col not in (('date_time_utc', ''), (MmxColumns.STATION_ID, ''), ('date_time_local', ''))
                     else ''.join(col).strip()
                     for col in df.columns.values]
    return df_return


def set_multilevel(df):
    groups = set()
    sensors = set()
    others = set()
    for column in df.columns:

        if column in (MmxColumns.STATION_ID, 'date_time', 'upper_t_road', 'lower_t_road'):
            others.add(column)
        else:
            (group, sensor) = column.split('_', 1)
            groups.add(group)
            sensors.add(sensor)

    columns = [(group, sensor) for group in groups for sensor in sensors
               if not ((group in ('id', 'valid')) and (sensor in ('azimuth', 'altitude')))]

    columns = pd.MultiIndex.from_tuples(columns)
    ret = pd.DataFrame(columns=columns)

    for column in columns:
        ret[column] = df['{0}_{1}'.format(column[0], column[1])]
    for column in others:
        ret[column] = df['{0}'.format(column)]
    ret.rename(columns={'total': 'total_indices'}, inplace=True)
    return ret
#--------------------------------------------------------------------------

class Preprocessor():

    def __init__(self):
        pass

    def SelectFeatures(self, df, features):
        return df[df['type'].isin(features)]

    def AddUTC(self, df_raw, station_def_path='/mnt/HARD/MinMax94/data/data_all/CSV/stations_mm94_def.csv'):

        station_def = pd.read_csv(station_def_path)

        def utc_time(df, station_id):
            timezone = station_def['timezone'][station_def[MmxColumns.STATION_ID] == station_id].values[0]
            df['date_time_utc'] = df['date_time'] - pd.Timedelta(str(timezone) + 'h')
            df = df.rename(columns={'date_time': 'date_time_local'})
            return df

        df_with_utc = df_raw.groupby(MmxColumns.STATION_ID).apply(lambda df: utc_time(df, df.name))
        return df_with_utc

    def PivotTable(self, df):
        upper_columns = [col for col in df.columns if col in ('data', 'id', 'valid')]
        df_pivoted = df.pivot_table(index=[MmxColumns.STATION_ID, 'date_time_utc', 'date_time_local'], columns='type', values=upper_columns)
        df_pivoted = df_pivoted.reset_index()
        df_pivoted.columns.names = [None] * len(df_pivoted.columns.names)
        df_pivoted = set_onelevel(df_pivoted)
        return df_pivoted

    def FixPressureScale(self, df_pivoted):
        if MmxColumns.PRESSURE in df_pivoted.columns:
            df_pivoted[MmxColumns.PRESSURE] = np.where((df_pivoted[MmxColumns.PRESSURE] > 700) & (df_pivoted[(MmxColumns.PRESSURE)] < 800),
                                           df_pivoted[(MmxColumns.PRESSURE)] * 10, df_pivoted[(MmxColumns.PRESSURE)])
        return df_pivoted

    def ConvertDataToMM94(self, df):
        for key in mapper_converter_to_mm94_column.keys():
            if key in df.columns:
                df[key] = mapper_converter_to_mm94_column[key](df[key])
        return df


    def CreatePatternList(self, df_pivoted, max_gap=pd.Timedelta('2h'), min_length=pd.Timedelta('12h')):
        pattern_list = [g for _, g in df_pivoted.groupby([MmxColumns.STATION_ID, (df_pivoted.date_time_utc.diff() > max_gap).cumsum()])
                            if g.date_time_utc.iloc[-1] - g.date_time_utc.iloc[0] > min_length]
        df_patterns = pd.concat(pattern_list)
        return df_patterns

    
    def InterpolatePatterns(self, df_patterns):

        id_columns = [column for column in df_patterns.columns if column.startswith('id_')]
        data_columns = [column for column in df_patterns.columns if column.startswith('data_')]

        data_integer_columns = [column for column in data_columns if column in ('data_cloudiness', 'data_precip_code')]
        data_continuous_columns = [column for column in data_columns if column not in data_integer_columns]

        def interpolate(df):

            df_result = deepcopy(df)
            df_result = df_result.set_index('date_time_utc')
            df_result['interpol'] = False

            # create table with rounded date_time
            start = df_result.index.min().round('30min')
            end = df_result.index.max().round('30min')

            start_loc = df_result.date_time_local.min().round('30min')
            end_loc = df_result.date_time_local.max().round('30min')

            df_add = pd.DataFrame(index=pd.date_range(start, end, freq='30min', name='date_time_utc'))
            df_add['interpol'] = True
            df_add['date_time_local'] = pd.date_range(start_loc, end_loc, freq='30min', name='date_time_local')
            df_add[MmxColumns.STATION_ID] = df_result[MmxColumns.STATION_ID].unique()[0]

            df_result = df_result.merge(df_add, how='outer', on=[MmxColumns.STATION_ID, 'interpol', 'date_time_local'], left_index=True,
                                        right_index=True, sort=True)

            for column in data_continuous_columns:
                df_result[column] = df_result[column].interpolate(method='linear', limit_directiom='both', limit=6)

            for column in data_integer_columns:
                if column == MmxColumns.CLOUDINESS:
                    df_result[column] = df_result[column].interpolate(method='linear', limit_directiom='both', limit=6).round()

                if column == MmxColumns.PRECIPITATION_CODE:
                    df_result[column] = df_result[column].interpolate(method='nearest', limit_directiom='both', limit=6)


            for column in id_columns:
                df_result[column] = df_result[column].interpolate(method='nearest', limit_direction='both', limit=6)

            df_result = df_result[df_result['interpol']]
            del df_result['interpol']
            df_result = df_result.dropna(thresh=3, subset=data_columns)
            df_result = df_result.reset_index()
            return df_result

        df_interpolated = df_patterns.groupby(MmxColumns.STATION_ID).apply(interpolate).reset_index(level=MmxColumns.STATION_ID, drop=True)
        return df_interpolated
