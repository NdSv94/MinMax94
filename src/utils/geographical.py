import pandas as pd
from geopy import distance
from constants import data_directory


def vincenty_dist(point_1, point_2):
    """point = tuple(lat, long)"""
    return distance.vincenty(point_1, point_2).km


def find_nearest_wmo_station(mm94_station_id):
    stations_mm94 = pd.read_csv(data_directory + '/stations_mm94_def.csv')
    stations_rp5 = pd.read_csv(data_directory + '/stations_rp5_def.csv')

    station_data = stations_mm94[stations_mm94['station_id'] == mm94_station_id]
    mm94_coords = station_data[['longitude', 'latitude']].values[0]

    wmo_station_id = stations_rp5.loc[[stations_rp5.apply(
        lambda x: vincenty_dist(mm94_coords, (x['longitude'], x['latitude'])),
        axis=1).idxmin()]]['station_id'].values[0]

    return wmo_station_id
