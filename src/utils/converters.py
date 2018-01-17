import pandas as pd
from copy import deepcopy
from constants import mapper_columns_rp5_to_mmx, RP5Columns, mapper_converter_to_rp5_column, MmxColumns

def rp5_datetime_to_mmx_format(datetime_rp5):
    date, time = datetime_rp5.split(' ')
    date = '-'.join(date.split('.')[::-1])
    time = time + ':00'
    datetime_standard = date + ' ' + time
    return datetime_standard

def mmx_datetime_to_metro_format(date_time):
    return str(date_time).rsplit(":", maxsplit=1)[0] + ' UTC'

def rename_columns_rp5_to_mmx(df_rp5):
    renaming_columns_dict = deepcopy(mapper_columns_rp5_to_mmx)

    cols_to_use = [RP5Columns.__getattribute__(RP5Columns, attr) for attr in RP5Columns.__dict__.keys()
                   if not attr.startswith('_')]
    df_rp5 = df_rp5[cols_to_use]
    df_rp5 = df_rp5.rename(columns=renaming_columns_dict)
    return df_rp5

def convert_rp5_to_mmx(df_rp5):

    df = deepcopy(df_rp5)

    # rename columns
    df = rename_columns_rp5_to_mmx(df)

    # convert date_time to Timestamp format
    df['date_time'] = pd.to_datetime(df['date_time'].apply(rp5_datetime_to_mmx_format))

    # convert rp5 values to mmx
    for column in df.columns:
        if column in mapper_converter_to_rp5_column.keys():
            df[column] = mapper_converter_to_rp5_column[column](df)

    # sort by date_time
    df = df.groupby(MmxColumns.STATION_ID).apply(lambda x: x.sort_values('date_time')).reset_index(drop=True)

    return df

def convert_mmx_to_metro(df_mmx):

    df = deepcopy(df_mmx)

    # rename columns
    df = rename_columns_rp5_to_mmx(df)

    # convert date_time to Timestamp format
    df['date_time'] = pd.to_datetime(df['date_time'].apply(rp5_datetime_to_mmx_format))

    # convert rp5 values to mmx
    for column in df.columns:
        if column in mapper_converter_to_rp5_column.keys():
            df[column] = mapper_converter_to_rp5_column[column](df)

    # sort by date_time
    df = df.groupby(MmxColumns.STATION_ID).apply(lambda x: x.sort_values('date_time')).reset_index(drop=True)

    return df