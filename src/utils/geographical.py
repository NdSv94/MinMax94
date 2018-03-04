import pandas as pd
from geopy import distance
from constants import data_directory
from constants import MmxColumns
import numpy as np


def vincenty_dist(point_1, point_2):
    """point = tuple(lat, long)"""
    return distance.vincenty(point_1, point_2).km


def find_nearest_wmo_station(mm94_station_id, verbose=False):
    stations_mm94 = pd.read_csv(data_directory + '/stations_mm94_def.csv')
    stations_rp5 = pd.read_csv(data_directory + '/stations_rp5_def.csv')

    station_data = stations_mm94[stations_mm94['station_id'] == mm94_station_id]
    mm94_coords = station_data[['latitude', 'longitude']].values[0]

    wmo_station_id = stations_rp5.loc[[stations_rp5.apply(
        lambda x: vincenty_dist(mm94_coords, (x['latitude'], x['longitude'])),
        axis=1).idxmin()]]['station_id'].values[0]
    wmo_data = stations_rp5[stations_rp5['station_id'] == wmo_station_id]
    wmo_coords = wmo_data[['latitude', 'longitude']].values[0]

    min_distance = stations_rp5.apply(
        lambda x: vincenty_dist(mm94_coords, (x['latitude'], x['longitude'])),
        axis=1).min()
    if verbose:
        print('distance({0}, {1}) = {2:0.2f} km'.format(mm94_coords, wmo_coords, min_distance))

    return wmo_station_id


def add_solar_angles(df_mmx):
    station_def = pd.read_csv(data_directory + '/stations_mm94_def.csv',
                              usecols=['station_id', 'longitude', 'latitude'])

    df = pd.merge(df_mmx, station_def, how='left', on=MmxColumns.STATION_ID)

    # calculate local astronomic time using utc_time and longitude
    df['astronomic_time'] = df[MmxColumns.DATE_TIME_UTC] + pd.to_timedelta((df['longitude'] // 15), unit='h')

    n_days = df['astronomic_time'].dt.dayofyear
    d = (360 * (n_days - 1) / 365)
    d_rad = d * np.pi / 180
    et = 9.87 * np.sin(2 * d_rad) + 7.53 * np.cos(d_rad) - 1.5 * np.sin(d_rad)

    lstm = 15 * (df['longitude'] // 15)

    add = - 4 * (lstm - df['longitude']) + et
    ast = df['astronomic_time'] + pd.to_timedelta(add, 'm')

    h = ((ast.dt.hour * 60 + ast.dt.minute) - 720) / 4
    h_rad = h * np.pi / 180

    lat_rad = df['latitude'] * np.pi / 180
    delta = 23.45 * np.sin((n_days + 284) / 365 * 360 / 180 * np.pi)
    delta_rad = delta * np.pi / 180

    sin_alt = np.cos(lat_rad) * np.cos(delta_rad) * np.cos(h_rad) + np.sin(lat_rad) * np.sin(delta_rad)
    solar_altitude = np.arcsin(sin_alt)

    cos_az = (sin_alt * np.sin(lat_rad) - np.sin(delta_rad)) / (np.cos(solar_altitude) * np.cos(lat_rad))
    solar_azimuth = np.arccos(cos_az) * np.sign(h_rad)

    return solar_azimuth, solar_altitude


def add_coordinates(df_mmx):
    station_def = pd.read_csv(data_directory + '/stations_mm94_def.csv',
                              usecols=['station_id', 'longitude', 'latitude'])

    df = pd.merge(df_mmx, station_def, how='left', on=MmxColumns.STATION_ID)

    return df['latitude'], df['longitude']


def add_road_id(df_mmx):
    station_def = pd.read_csv(data_directory + '/stations_mm94_def.csv',
                              usecols=['station_id', 'road_id'])

    df = pd.merge(df_mmx, station_def, how='left', on=MmxColumns.STATION_ID)

    return df['road_id']
