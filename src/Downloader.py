import pandas as pd

class Extractor():
    def __init__(self, station_list, sensor_list, start, end):
        self.station_list = station_list
        self.sensor_list = sensor_list
        self.start = start
        self.end = end

    def ExtractFromFile(self, path='./data_csv/full_raw.csv'):
        dateparse = pd.to_datetime
        df = pd.read_csv(path, index_col=0, dtype = {'station_id': int, 'date_time': str},
                        date_parser = dateparse, parse_dates = ['date_time'])

        if self.station_list is not None:
            df = df[df['station_id'].isin(self.station_list)]

        if self.sensor_list is not None:
            df = df[df['sensor_type_id'].isin(self.sensor_list)]

        if self.start is not None:
            df = df[df['date_time'] >= self.start]

        if self.end is not None:
            df = df[df['date_time'] <= self.end]

        return df.reset_index(drop=True)

    def ExtractFromDB(self, db_connection='mysql://root:casper@127.0.0.1:3306/lmeteo3', limit=None):

        sql_query = 'select station_data.station_id, date_time, data, sensor_type_id, type' + \
                    ' from sensor_data, sensor_def, station_data, sensor_type' + \
                    ' where '

        if self.station_list is not None:
            sql_query += 'station_data.station_id in (' + str(self.station_list)[1:-1] + ') '
        else:
            sql_query += 'true '

        if self.start is not None:
            sql_query += 'and station_data.date_time >\'' + str(self.start) + '\' '

        if self.end is not None:
            sql_query += 'and station_data.date_time <\'' + str(self.end) + '\' '

        if self.sensor_list is not None:
            sql_query += 'and sensor_def.sensor_type_id in (' + str(self.sensor_list)[1:-1] + ') '

        sql_query += 'and sensor_def.id = sensor_data.sensor_id' + \
                     ' and station_data.id = sensor_data.station_data_id' + \
                     ' and sensor_type.id = sensor_def.sensor_type_id '

        if limit is not None:
            sql_query += 'limit ' + str(limit)
        sql_query += ';'

        df = pd.read_sql(con=db_connection, sql=sql_query)
        return df

    def ExtractFromStream(self):
        pass

    def ExtractPivotedTable(self, path='./data_csv/meteo_splitted.csv'):
        dateparse = pd.to_datetime
        df = pd.read_csv(path, index_col=0,
                                     dtype={'station_id': int, 'date_time': str},
                                     date_parser=dateparse,
                                     parse_dates=['date_time'])
        if self.station_list is not None:
            df = df[df['station_id'].isin(self.station_list)]

        #if self.sensor_list is not None:
        #   df = df[df['sensor_type_id'].isin(self.sensor_list)]

        if self.start is not None:
            df = df[df['date_time'] >= self.start]

        if self.end is not None:
            df = df[df['date_time'] <= self.end]

        return df.reset_index(drop=True)