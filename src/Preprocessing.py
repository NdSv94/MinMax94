import numpy as np
import pandas as pd
import datetime
from copy import deepcopy
from tqdm import tqdm_notebook
import re

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

def UnLagTable(df_lagged):
    df = df_lagged.loc[:, df_lagged.columns.get_level_values(1).isin({0})]
    df.columns = df.columns.droplevel('lag')
    df = set_multilevel(df)
    return df


def verify_geoloc(geoloc):
    verify = True
    pattern = "^([0-9]|([0-9][0-9])) ([0-9]|([0-9][0-9])) ([0-9]|([0-9][0-9]))$"
    if (not re.match(pattern, geoloc)) or geoloc == '0 0 0':
        verify = False
    return verify

#--------------------------------------------------------------------------

class Preprocessor():

    def __init__(self):
        pass

    def PivotTable(self, df):
        df_pivoted = df.pivot_table(index=['station_id', 'date_time'], columns='type', values=['data', 'id', 'valid'])
        df_pivoted = df_pivoted.reset_index()
        #del df_pivoted.columns.name
        df_pivoted.columns.names = [None] * len(df_pivoted.columns.names)
        return df_pivoted

    def FixPressureScale(self, df_pivoted):
        if 'pressure' in df_pivoted.columns.levels[1]:
            df_pivoted[('data', 'pressure')] = np.where((df_pivoted[('data', 'pressure')] > 700) & (df_pivoted[('data', 'pressure')] < 800),
                                           df_pivoted[('data', 'pressure')] * 10, df_pivoted[('data', 'pressure')])
        return df_pivoted

    def CreatePatternList(self, df_pivoted, max_gap=pd.Timedelta('2h'), min_length=pd.Timedelta('12h')):
        pattern_list = [g for _, g in df_pivoted.groupby(['station_id', (df_pivoted.date_time.diff() > max_gap).cumsum()])
                            if g.date_time.iloc[-1] - g.date_time.iloc[0] > min_length]
        return pattern_list

    def InterpolatePatterns(self, pattern_list):

        def round_30min(time):
            return datetime.datetime(time.year, time.month, time.day, time.hour, time.minute - time.minute % 30, 0)

        def interpolate(df):
            # copy the initial dataframe, so that no actions inside the function can affect it
            df_result = deepcopy(df)

            start = round_30min(df_result.date_time.min())
            end = round_30min(df_result.date_time.max())

            df_add = pd.DataFrame(pd.date_range(start=start, end=end, freq='30min'),
                                  columns=pd.MultiIndex.from_tuples([('date_time', '')]))

            # !!if len(df_result.station_id.unique()) > 1 --- Raise Error ##
            df_add[('station_id', '')] = df_result.station_id.unique()[0]

            # adding a new column, so that we can define, which data is original and which is interpolated
            df_result[('interpol', '')] = False
            df_add[('interpol', '')] = True

            # Merging 2 tables
            df_result = pd.merge(df_result, df_add, how='outer',
                                 on=['date_time', 'interpol', 'station_id'])

            df_result = df_result.set_index('date_time')
            df_result = df_result.sort_index()
            df_result.valid = True

            # Interpolating data in '30min - round' timestamp
            df_result.data = df_result.data.interpolate(method='time', limit_direction='both')
            df_result.id = df_result.id.interpolate(method='nearest', limit_direction='both')

            # Deleting original data, leaving only interpolated rows
            df_result = df_result[df_result.interpol]
            del df_result[('interpol',)]
            df_result = df_result.dropna()
            df_result = df_result.reset_index()
            return df_result

        patterns_interpolated = [interpolate(pattern) for pattern in tqdm_notebook(pattern_list)]

        return patterns_interpolated

    def CreateLaggedTable(self, patterns_interpolated, lag_range = np.arange(-6, 4.5, 0.5)):

        def create_lagged_table(df, lag_range=lag_range):
            df = set_onelevel(df)
            features = [col for col in df.columns if col.startswith('data_')]
            feature_tuples = [(feature, lag) for feature in features for lag in lag_range]

            others = [col for col in df.columns if col not in features]
            info_tuples = [(other, 0) for other in others]

            columns = feature_tuples + info_tuples
            micolumns = pd.MultiIndex.from_tuples(columns, names=['feature', 'lag'])
            df_lagged = pd.DataFrame(columns=micolumns)

            for column in df.columns:
                if column in features:
                    series = df[column]
                    for lag in lag_range:
                        lagged_series = series.shift(int(-lag * 2))
                        df_lagged[(column, lag)] = lagged_series

                elif column in others:
                    df_lagged[(column, 0)] = df[column]

            df_lagged = df_lagged.dropna()
            return df_lagged

        patterns_final = [create_lagged_table(pattern) for pattern in tqdm_notebook(patterns_interpolated)]
        return patterns_final
