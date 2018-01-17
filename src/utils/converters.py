import pandas as pd
from copy import deepcopy
from constants import field_converter_rp5_to_mmx, RP5Columns, data_converter_rp5_to_mmx, MmxColumns

def convert_data(df, data_converter_dict):
    for column in df.columns:
        if column in data_converter_dict.keys():
            df[column] = data_converter_dict[column](df)
    return df

def rename_fields(df, field_converter_dict):
    df = df.rename(columns=field_converter_dict)
    return df

def convert_format(df, from_format='RP5', to_format='Mmx'):

    if ((from_format=='RP5') and (to_format=='Mmx')):
        field_converter_dict = field_converter_rp5_to_mmx
        data_converter_dict = data_converter_rp5_to_mmx
    else: raise ValueError("Convertating from {0} to {1} format is not supported!")

    df = rename_fields(df, field_converter_dict)
    df = convert_data(df, data_converter_dict)

    cols_to_use = [MmxColumns.__getattribute__(MmxColumns, attr) for attr in MmxColumns.__dict__.keys()
                   if not attr.startswith('__')]
    cols_to_use = [col for col in cols_to_use if col in df.columns]
    df = df[cols_to_use]
    return df