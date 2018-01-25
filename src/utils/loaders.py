import pandas as pd
import numpy as np
from copy import deepcopy
from converters import MmxColumns, RP5Columns
from constants import data_directory, rp5_columns, available_meteo_parameters


def select_mm94_features(df, features='all'):
    if features == 'all':
        features = available_meteo_parameters
    return df[df['type'].isin(features)]

def load_rp5_stations(wmo_stations_id):
    if isinstance(wmo_stations_id, np.int64):
        wmo_stations_id = [wmo_stations_id]

    loaded_stations_list = []

    for wmo_id in wmo_stations_id:
        rp5 = pd.read_csv(data_directory + '/RP5/' + str(wmo_id) + '.csv', sep=';', skiprows=6, index_col=False,
                          dtype={RP5Columns.VISIBILITY: str,
                                 RP5Columns.PRECIPITATION_INTENSITY: str})

        date_time_col = [col for col in rp5.columns if col.startswith('Местное время')][0]
        rp5 = rp5.rename(columns={date_time_col: 'Местное время'})
        rp5['station_id'] = int(wmo_id)

        # columns which are absent for the exact wmo station
        absent_columns = [col for col in rp5_columns if col not in rp5.columns]
        rp5[absent_columns] = np.nan

        # leave only columns which are needed (from constants)
        rp5 = rp5[rp5_columns]
        loaded_stations_list.append(rp5)

    rp5_stations = pd.concat(loaded_stations_list)
    rp5_stations = rp5_stations.reset_index(drop=True)
    return rp5_stations


def load_mm94_stations(mm94_stations_id, features_list='all'):
    if isinstance(mm94_stations_id, int):
        mm94_stations_id = [mm94_stations_id]

    loaded_stations_list = []
    for station_id in mm94_stations_id:
        raw = pd.read_csv(data_directory + '/MM94/' + str(station_id) + '_raw.csv', parse_dates=['date_time'])
        raw = select_mm94_features(raw, features=features_list)
        loaded_stations_list.append(raw)
    raw_stations = pd.concat(loaded_stations_list)
    raw_stations = raw_stations.reset_index(drop=True)
    return raw_stations
