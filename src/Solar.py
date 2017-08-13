import pandas as pd
from copy import deepcopy
from tqdm import tqdm_notebook
import ephem
import re


def grad(lst):
    return lst[0] + lst[1] / 60 + lst[2] / 3600


def solar_angles(lat, lon, date_time):
    lat = grad([int(elem) for elem in lat.split(' ')])
    lon = grad([int(elem) for elem in lon.split(' ')])
    gatech = ephem.Observer()
    sun = ephem.Sun()
    gatech.lat, gatech.lon, gatech.date = str(lat), str(lon), date_time
    sun.compute(gatech)
    return sun.alt, sun.az


def verify_geoloc(geoloc):
    verify = True
    pattern = "^([0-9]{1,2} ){2}([0-9]{1,2})$"
    if (not re.match(pattern, geoloc)) or geoloc == '0 0 0':
        verify = False
    return verify


def AddSolarAngles(patterns_interpolated, solar_data_path="/home/ndsviriden/data_csv/station_def.csv"):
    station_def = pd.read_csv(solar_data_path, encoding='cp1251', na_values=r'\N',
                              usecols=['station_id', 'latitude', 'longitude'])
    station_def = station_def.dropna()
    station_def = station_def[station_def['latitude'].apply(verify_geoloc)]
    station_def = station_def[station_def['longitude'].apply(verify_geoloc)]

    cols = [('station_id', ''), ('data', 'latitude'), ('data', 'longitude')]
    micolumns = pd.MultiIndex.from_tuples(cols)
    station_def.columns = micolumns

    def solar_to_pattern(df):
        df_solar = deepcopy(df)
        df_solar = pd.merge(df_solar, station_def, 'inner', on=[('station_id',)])

        if not df_solar.empty:
            df_solar[('data', 'altitude')] = df_solar.apply(lambda row: solar_angles(row[('data', 'latitude')],
                                                                                     row[('data', 'longitude')],
                                                                                     row[('date_time', '')])[0], axis=1)

            df_solar[('data', 'azimuth')] = df_solar.apply(lambda row: solar_angles(row[('data', 'latitude')],
                                                                                    row[('data', 'longitude')],
                                                                                    row[('date_time', '')])[1], axis=1)
            del df_solar[('data', 'latitude')]
            del df_solar[('data', 'longitude')]
            df_solar = df_solar.sort_index(axis=1)
        return df_solar


    patterns_with_angles = [solar_to_pattern(pattern) for pattern in tqdm_notebook(patterns_interpolated) if
                            (not pattern.empty)]
    patterns_with_angles = [pattern for pattern in patterns_with_angles if (len(pattern) > 0)]

    return patterns_with_angles
