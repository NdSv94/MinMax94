import pandas as pd
import MySQLdb
import json
from date_time_handlers import parse_timezone_from_db


def extract_mm94_meteo_data(station_list, start, end, sensor_list=(1, 2, 3, 4, 16),
                            db_connection='mysql://root:casper@127.0.0.1:3306/lmeteo3', limit=None):
    sql_query = 'select sensor_data.id as "id", station_data.station_id, date_time, ' + \
                'data, sensor_type_id, type, sensor_def.id as "sensor_id", active_state ' + \
                'from sensor_data, sensor_def, station_data, sensor_type ' + \
                'where '

    if station_list is not None:
        sql_query += 'station_data.station_id in (' + str(station_list)[1:-1] + ') '
    else:
        sql_query += 'true '

    if start is not None:
        sql_query += 'and station_data.date_time >\'' + str(start) + '\' '

    if end is not None:
        sql_query += 'and station_data.date_time <\'' + str(end) + '\' '

    if sensor_list is not None:
        sql_query += 'and sensor_def.sensor_type_id in (' + str(sensor_list)[1:-1] + ') '

    sql_query += 'and sensor_def.id = sensor_data.sensor_id ' + \
                 'and station_data.id = sensor_data.station_data_id ' + \
                 'and sensor_type.id = sensor_def.sensor_type_id '

    if limit is not None:
        sql_query += 'limit ' + str(limit)
    sql_query += ';'
    df = pd.read_sql(con=db_connection, sql=sql_query)
    return df


def extract_mm94_station_info(host="192.168.1.230", user='lm_ro', passwd='lm_rovtntj', port=3306):
    db = MySQLdb.connect(host,
                         user=user,
                         passwd=passwd,
                         port=port,
                         db='cup_system3')

    # utf-8 encoding
    db.set_character_set("utf8")
    dbc = db.cursor()

    sql_query = "SELECT  meteo_table.*, " + \
                "objects.id AS video_id, " + \
                "objects.properties AS video_properties " + \
                "FROM objects " + \
                "RIGHT JOIN " + \
                "(SELECT  objects.id AS station_id, " + \
                "objects.place_id AS place_id, " + \
                "roads.id AS road_id, " + \
                "places.address, " + \
                "CONCAT('км ', places.address, '+', places.meters, ' а/д ' , roads.short_name) AS name, " + \
                "places.latitude, " + \
                "places.longitude, " + \
                "places.height AS altitude, " + \
                "objects.properties " + \
                "FROM objects, places, roads " + \
                "WHERE objects.type = 1 " + \
                "AND objects.place_id = places.id " + \
                "AND places.road_id = roads.id) AS meteo_table " + \
                "ON meteo_table.place_id = objects.place_id " + \
                "WHERE objects.type = 2;"

    # SELECT for cyrillic fields
    dbc.execute(sql_query)

    # getting the results
    data = dbc.fetchall()

    columns = ['station_id', 'place_id', 'road_id', 'km', 'place', 'latitude', 'longitude', 'altitude',
               'properties', 'video_id', 'video_properties']

    # creating pandas table with column names from above
    df = pd.DataFrame(list(data), columns=columns)
    df['timezone'] = df['properties'].apply(parse_timezone_from_db)
    df['video_timezone'] = df['video_properties'].apply(parse_timezone_from_db)
    df['video_path'] = df['video_properties'].apply(lambda row: json.loads(row)["dir"])
    del df['properties'], df['video_properties']
    return df


def extract_mm94_video_data(station_list, db_connection='mysql://root:casper@127.0.0.1:3306/cup_video2'):

    sql_query = "SELECT id, datetime_ins as date_time, station_num as video_id, data as path" + \
                " FROM cup_video2.pic_data WHERE station_num IN {0};".format(tuple(station_list))

    df = pd.read_sql(con=db_connection, sql=sql_query)
    return df

