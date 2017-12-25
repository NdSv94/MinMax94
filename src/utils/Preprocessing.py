import numpy as np
import pandas as pd
from copy import deepcopy
from tqdm import tqdm_notebook

def set_onelevel(df):
    df_return = deepcopy(df)
    df_return.columns = ['_'.join(col).strip() if col not in (('date_time', ''), ('station_id', ''))
                     else ''.join(col).strip()
                     for col in df.columns.values]
    return df_return


def set_multilevel(df):
    groups = set()
    sensors = set()
    others = set()
    for column in df.columns:

        if column in ('station_id', 'date_time', 'upper_t_road', 'lower_t_road'):
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

    def PivotTable(self, df):
        upper_columns = [col for col in df.columns if col in ('data', 'id', 'valid')]
        df_pivoted = df.pivot_table(index=['station_id', 'date_time'], columns='type', values=upper_columns)
        df_pivoted = df_pivoted.reset_index()
        df_pivoted.columns.names = [None] * len(df_pivoted.columns.names)
        df_pivoted = set_onelevel(df_pivoted)
        return df_pivoted

    def FixPressureScale(self, df_pivoted):
        if 'data_pressure' in df_pivoted.columns:
            df_pivoted['data_pressure'] = np.where((df_pivoted['data_pressure'] > 700) & (df_pivoted[('data_pressure')] < 800),
                                           df_pivoted[('data_pressure')] * 10, df_pivoted[('data_pressure')])
        return df_pivoted

    def CreatePatternList(self, df_pivoted, max_gap=pd.Timedelta('2h'), min_length=pd.Timedelta('12h')):
        pattern_list = [g for _, g in df_pivoted.groupby(['station_id', (df_pivoted.date_time.diff() > max_gap).cumsum()])
                            if g.date_time.iloc[-1] - g.date_time.iloc[0] > min_length]
        df_patterns = pd.concat(pattern_list)
        return df_patterns

    
    def InterpolatePatterns(self, df_patterns):

        data_columns = [column for column in df_patterns.columns if column.startswith('data_')]
        id_columns = [column for column in df_patterns.columns if column.startswith('id_')]

        def interpolate(df):
            # copy the initial dataframe, so that no actions inside the function can affect it

            df_result = deepcopy(df)
            df_result = df_result.set_index('date_time')
            df_result['interpol'] = False

            # create table with rounded date_time
            start = df_result.index.min().round('30min')
            end = df_result.index.max().round('30min')
            df_add = pd.DataFrame(index=pd.date_range(start, end, freq='30min', name='date_time'))
            df_add['interpol'] = True
            df_add['station_id'] = df_result['station_id'].unique()[0]

            df_result = df_result.merge(df_add, how='outer', on=['station_id', 'interpol'], left_index=True,
                                        right_index=True, sort=True)

            for column in data_columns:
                df_result[column] = df_result[column].interpolate(method='linear', limit_directiom='both', limit=6)
            for column in id_columns:
                df_result[column] = df_result[column].interpolate(method='nearest', limit_direction='both', limit=6)

            df_result = df_result[df_result['interpol']]
            del df_result['interpol']
            df_result = df_result.dropna(thresh=3, subset=data_columns)
            return df_result

        df_interpolated = df_patterns.groupby('station_id').apply(interpolate).reset_index(level='station_id', drop=True)
        return df_interpolated
