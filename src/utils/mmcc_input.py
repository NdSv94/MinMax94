import pandas as pd
from copy import copy
from constants import RUSSIAN_TIME_ZONES, data_directory, ROAD_LAYERS, CATEGORY, \
    ROAD_CATEGORY, MAINTAINABILITY_LEVEL
from constants import HOURS_BEFORE_PREDICTION, FORECAST_HOURS_AFTER_PREDICTION, FORECAST_HOURS_BEFORE_PREDICTION
from constants import MmccForecastColumns, MmccRwisColumns
import requests
from time import sleep
import json


def get_station_config(mm94_station_id):
    stations_mm94 = pd.read_csv(data_directory + '/stations_mm94_def.csv')
    station_data = stations_mm94[stations_mm94['station_id'] == mm94_station_id]

    station_config = {"station_nature": "real",
                      "station_type": "road",
                      "road_category": ROAD_CATEGORY,
                      "roadlayers": ROAD_LAYERS,
                      "timezone": RUSSIAN_TIME_ZONES[station_data["timezone"].values[0]],
                      "station_id": mm94_station_id,
                      "latitude": station_data["latitude"].values[0],
                      "longitude": station_data["longitude"].values[0]}

    return station_config


def get_road_config(mm94_station_id):
    road_config = {"maintainability_level": MAINTAINABILITY_LEVEL,
                   "category": CATEGORY}

    return road_config


def get_rwis_data_json(df_rwis, time_record):
    hours_before_prediction = pd.Timedelta(HOURS_BEFORE_PREDICTION, unit='h')
    df = copy(df_rwis)
    start = time_record - hours_before_prediction
    end = time_record
    rwis_data = df[(df.index >= start) & (df.index <= end)]
    rwis_data = rwis_data.set_index(MmccRwisColumns.DATE_TIME_METRO, drop=True)
    del rwis_data[MmccRwisColumns.STATION_ID]
    rwis_data[MmccRwisColumns.FREEZING_POINT] = 0
    rwis_data_json = rwis_data.to_dict(orient='index')
    return rwis_data_json


def get_global_forecast_json(df_forecast, time_record):
    forecast_hours_before = pd.Timedelta(FORECAST_HOURS_BEFORE_PREDICTION, unit='h')
    forecast_hours_after = pd.Timedelta(FORECAST_HOURS_AFTER_PREDICTION, unit='h')
    df = copy(df_forecast)

    start = time_record - forecast_hours_before
    end = time_record + forecast_hours_after
    global_forecast = df[(df.index >= start) & (df.index <= end)]
    global_forecast = global_forecast.set_index(MmccForecastColumns.DATE_TIME_METRO, drop=True)
    del global_forecast[MmccForecastColumns.STATION_ID]
    global_forecast_json = global_forecast.to_dict(orient='index')

    for k, v in global_forecast_json.items():
        global_forecast_json[k]['cloudiness'] = int(global_forecast_json[k]['cloudiness'])

    return global_forecast_json


def get_mmcc_input_json(station_id, df_rwis, df_forecast, time_record):
    station_config = get_station_config(station_id)
    road_config = get_road_config(station_id)

    rwis_data_json = get_rwis_data_json(df_rwis, time_record)
    global_forecast_json = get_global_forecast_json(df_forecast, time_record)
    mmcc_input_json = {"station_config": station_config,
                       "road_config": road_config,
                       "global_forecast": global_forecast_json,
                       "rwis_data": rwis_data_json}

    return mmcc_input_json


def get_mmcc_prediction(mmcc_input_json, url_roadcast='http://127.0.0.1:5000/roadcast',
                        url_calc='http://127.0.0.1:5000/calculation'):

    with requests.Session() as session:
        session.headers = {'Content-type': 'application/json', 'Host': ".api.mmcc.pkcup.ru",
                           'cache-control': "no-cache",  # 'postman-token': '727b926f-c7b5-854e-06d7-bea9df150a12',
                           'User-Agent': 'test'}

        response_post = session.post(url_calc, params={"key": "MeAuthKeyMeSmart"}, json=mmcc_input_json)
        # sleep(4)  # What should I do with it

        flag = True
        i = 0

        while flag:
            sleep(0.1)
            i += 1

            try:
                job_id = json.loads(response_post.text)['job_id']
                response_get = session.get(url_roadcast,
                                           params={"job_id": job_id, "key": "MeAuthKeyMeSmart"}, timeout=5)
                mmcc_prediction = response_get.content
                mmcc_prediction = json.loads(mmcc_prediction.decode('utf-8'))

                if mmcc_prediction['roadcast']:
                    flag = False
                    # print(i * 0.1, 'seconds')

            except KeyError:
                print(response_post.content)
                # print('-------------------')
                mmcc_prediction = {'emergency_report': None,
                                   'forecast_alerts': None,
                                   'roadcast': None,
                                   'roadcast_alerts': None}
                flag = False

            if i > 50:
                flag = False
                print('Too long to wait')
                # print(i * 0.1, 'seconds')

    # mmcc_prediction = response_get.content
    return mmcc_prediction
