from extractors_from_db import extract_mm94_video_data
import pandas as pd
from constants import data_directory
from os import listdir
from os.path import isfile, join
from tqdm import tqdm

station_list = pd.read_csv(join(data_directory, 'stations_mm94_def.csv'))
station_list = list(station_list['video_id'])
path_video = join(data_directory, 'VIDEO/')
step = 25
print(path_video)

stations_in_dir = [int(f.split('_', 1)[0]) for f in listdir(path_video)
                   if isfile(join(path_video, f)) if not f.startswith('.')]
stations_in_dir.sort()
print('Stations in directory: ', stations_in_dir)
stations_in_dir = set(stations_in_dir)
stations_to_extract = [station for station in station_list if station not in stations_in_dir]

for i in tqdm(range(0, len(stations_to_extract), step)):
    stations = stations_to_extract[i: i + step]
    print('Extracting stations: ', stations)
    df_raw = extract_mm94_video_data(stations)

    for station in stations:
        print('Writing data into ' + path_video + str(station) + '_video.csv')
        df_raw[df_raw['video_id'] == station].to_csv(path_video + str(station) + '_video.csv', index=False)
