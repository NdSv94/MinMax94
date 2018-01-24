import pandas as pd
import MySQLdb
import json

class ExtractorData():

    def __init__(self):
        pass


    def ExtractFromFile(self, station_list, start, end,
                        sensor_list=(1, 2, 3, 4, 16), path='./data_csv/full_raw.csv'):
        dateparse = pd.to_datetime
        df = pd.read_csv(path, index_col=0, dtype={'station_id': int, 'date_time': str},
                        date_parser = dateparse, parse_dates = ['date_time'])

        if station_list is not None:
            df = df[df['station_id'].isin(station_list)]

        if sensor_list is not None:
            df = df[df['sensor_type_id'].isin(sensor_list)]

        if start is not None:
            df = df[df['date_time'] >= start]

        if end is not None:
            df = df[df['date_time'] <= end]

        return df.reset_index(drop=True)

    def ExtractFromDB(self, station_list, start, end, sensor_list=(1, 2, 3, 4, 16),
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

    def ExtractFromStream(self):
        pass

###########################################################################################################
def parse_timezone(property_string):
    property_dict = json.loads(property_string)
    try:
        timezone_string = property_dict['raw_timezone']
    except KeyError: #deafult timezone is Moscow +3UTC (if no tz mentioned, so assume tz="+3UTC")
        timezone_string = '+3'

    sign = 2 *(timezone_string[0]=='+') - 1 # 1 -- eastern hemisphere, -1 -- western hemisphere
    return sign * int(timezone_string[1:])


class ExtractorStationInfo():
    def __init__(self):
        pass

    def ExtractFromDB(self, host="192.168.1.230", user='lm_ro', passwd='lm_rovtntj', port=3306):
        db = MySQLdb.connect(host,
                             user=user,
                             passwd=passwd,
                             port=port)

        # utf-8 encoding
        db.set_character_set("utf8")
        dbc = db.cursor()

        sql_query = "select objects.id as 'station_id', roads.id as 'road_id', places.address, " + \
                    "concat('км ', places.address, '+',places.meters, " + \
                    " ' а/д ' , roads.short_name) as 'name' ," + \
                    "places.latitude, places.longitude, places.height as 'altitude', " + \
                    "objects.properties " + \
                    "from cup_system3.objects, cup_system3.places, cup_system3.roads, lmeteo3.station_def " + \
                    "where lmeteo3.station_def.id = objects.id " + \
                    "and objects.place_id = places.id " + \
                    "and places.road_id = roads.id;"

        # SELECT for cyrillic fields
        dbc.execute(sql_query)

        # getting the results
        data = dbc.fetchall()

        columns = ['station_id', 'road_id', 'km', 'place', 'longitude', 'latitude', 'altitude', 'properties']

        # creating pandas table with column names from above
        df = pd.DataFrame(list(data), columns=columns)
        df['timezone'] = df['properties'].apply(parse_timezone)
        del df['properties']

        return df


