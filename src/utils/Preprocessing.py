import numpy as np
import pandas as pd
from copy import deepcopy
from constants import MmxColumns
from constants import field_converter_rp5_to_mmx, data_converter_rp5_to_mmx
from constants import field_converter_raw_to_mmx, data_converter_raw_to_mmx

def set_onelevel(df):
    df_return = deepcopy(df)
    df_return.columns = ['_'.join(col).strip()
                        if col not in ((MmxColumns.DATE_TIME_UTC, ''), (MmxColumns.STATION_ID, ''), (MmxColumns.DATE_TIME_LOCAL, ''))
                        else ''.join(col).strip() for col in df.columns.values]
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

def convert_data(df, data_converter_dict):
    for column in df.columns:
        if column in data_converter_dict.keys():
            df[column] = data_converter_dict[column](df)
    return df

def rename_fields(df, field_converter_dict):
    df = df.rename(columns=field_converter_dict)
    return df
#--------------------------------------------------------------------------

class Preprocessor():

    def __init__(self):
        pass

    def SelectFeatures(self, df, features):
        return df[df['type'].isin(features)]

    def PivotTable(self, df):
        upper_columns = [col for col in df.columns if col in ('data', 'id', 'valid')]
        df_pivoted = df.pivot_table(index=[MmxColumns.STATION_ID, MmxColumns.DATE_TIME_LOCAL], columns='type', values=upper_columns)
        df_pivoted = df_pivoted.reset_index()
        df_pivoted.columns.names = [None] * len(df_pivoted.columns.names)
        df_pivoted = set_onelevel(df_pivoted)
        return df_pivoted

    def ConvertData(self, df, from_format='RP5', to_format='Mmx'):
        if ((from_format == 'RP5') and (to_format == 'Mmx')):
            field_converter_dict = field_converter_rp5_to_mmx
            data_converter_dict = data_converter_rp5_to_mmx
        elif ((from_format == 'Raw') and (to_format == 'Mmx')):
            field_converter_dict = {}
            data_converter_dict = data_converter_raw_to_mmx
        else:
            raise ValueError("Converting from {0} to {1} format is not supported!".format(from_format, to_format))

        df = rename_fields(df, field_converter_dict)
        df = convert_data(df, data_converter_dict)

        cols_to_use = [MmxColumns.__getattribute__(MmxColumns, attr) for attr in MmxColumns.__dict__.keys()
                       if not attr.startswith('__')]
        cols_to_use = [col for col in cols_to_use if col in df.columns]
        df = df[cols_to_use]
        return df

    def AddUTC(self, df_raw, station_def_path='/mnt/HARD/MinMax94/data/data_all/CSV/stations_mm94_def.csv'):

        station_def = pd.read_csv(station_def_path)

        def utc_time(df, station_id):
            timezone = station_def['timezone'][station_def[MmxColumns.STATION_ID] == station_id].values[0]
            df[MmxColumns.DATE_TIME_UTC] = df[MmxColumns.DATE_TIME_LOCAL] - pd.Timedelta(str(timezone) + 'h')
            return df

        df_with_utc = df_raw.groupby(MmxColumns.STATION_ID).apply(lambda df: utc_time(df, df.name))
        return df_with_utc

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
            start = df_result.index.min().round('30min')
            end = df_result.index.max().round('30min')

            start_loc = df_result.date_time.min().round('30min')
            end_loc = df_result.date_time.max().round('30min')

            df_add = pd.DataFrame(index=pd.date_range(start, end, freq='30min', name=MmxColumns.DATE_TIME_UTC))
            df_add['interpol'] = True
            df_add[MmxColumns.DATE_TIME_LOCAL] = pd.date_range(start_loc, end_loc, freq='30min', name=MmxColumns.DATE_TIME_LOCAL)
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
