import pandas as pd
from copy import deepcopy
from constants import mapper_columns_rp5_to_mm94, RP5Columns, mapper_converter_to_column, MmxColumns

def parse_datetime_rp5(datetime_rp5):
    date, time = datetime_rp5.split(' ')
    date = '-'.join(date.split('.')[::-1])
    time = time + ':00'
    datetime_standard = date + ' ' + time
    return datetime_standard

def rename_columns_rp5_to_mm94(df_rp5):
    renaming_columns_dict = deepcopy(mapper_columns_rp5_to_mm94)
    initial_date_time_column = [column for column in df_rp5.columns if column.startswith("Местное время")][0]
    renaming_columns_dict[initial_date_time_column] = 'date_time'

    cols_to_use = [RP5Columns.__getattribute__(RP5Columns, attr) for attr in RP5Columns.__dict__.keys()
                   if not attr.startswith('_')] + [initial_date_time_column]
    df_rp5 = df_rp5[cols_to_use]
    df_rp5 = df_rp5.rename(columns=renaming_columns_dict)
    return df_rp5

def convert_rp5_to_mm94(df_rp5):

    df = deepcopy(df_rp5)

    # rename columns
    df = rename_columns_rp5_to_mm94(df)

    # convert date_time to Timestamp format
    df['date_time'] = pd.to_datetime(df['date_time'].apply(parse_datetime_rp5))

    # convert rp5 values to mm94
    for key in mapper_converter_to_column.keys():
        if key in df.columns:
            df[key] = mapper_converter_to_column[key](df[key])

    # count intensity in mm/hour
    df[MmxColumns.PRECIPITATION_INTENSITY] = df[MmxColumns.PRECIPITATION_INTENSITY] / df[MmxColumns.PRECIPITATION_INTERVAL]

    # sort by date_time
    df = df.groupby(MmxColumns.STATION_ID).apply(lambda x: x.sort_values('date_time')).reset_index(drop=True)

    return df