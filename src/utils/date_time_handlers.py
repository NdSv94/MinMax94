import pandas as pd
from copy import copy
from constants import MmxColumns, data_directory
import datetime
import pytz
from tzwhere import tzwhere
import json


def parse_timezone_from_db(property_string):
    property_dict = json.loads(property_string)
    try:
        timezone_string = property_dict['raw_timezone']

        if not timezone_string:
            timezone_string = '+3'

    except KeyError:  # default timezone is Moscow +3UTC (if no tz mentioned, so assume tz="+3UTC")
        timezone_string = '+3'

    sign = 2 * (timezone_string[0] == '+') - 1  # 1 -- eastern hemisphere, -1 -- western hemisphere
    return sign * int(timezone_string[1:])


def rp5_datetime_to_mmx_format(datetime_rp5):
    date, time = datetime_rp5.split(' ')
    date = '-'.join(date.split('.')[::-1])
    time = time + ':00'
    datetime_standard = date + ' ' + time
    return datetime_standard


def mmx_datetime_to_mmcc_format(date_time):
    return str(date_time).rsplit(":", maxsplit=1)[0] + ' UTC'


def add_utc(df_raw, station_def_path=data_directory + '/stations_mm94_def.csv'):
    df_todo = copy(df_raw)
    station_def = pd.read_csv(station_def_path)

    def utc_time(df, station_id):
        timezone = station_def['timezone'][station_def[MmxColumns.STATION_ID] == station_id].values[0]
        # print(station_id, timezone)
        df[MmxColumns.DATE_TIME_UTC] = pd.to_datetime(
            df[MmxColumns.DATE_TIME_LOCAL] - pd.Timedelta(str(timezone) + 'h'))
        return df

    date_time_utc = df_todo.groupby(MmxColumns.STATION_ID).apply(
        lambda df: utc_time(df, df.name)[[MmxColumns.DATE_TIME_UTC]])
    return date_time_utc


def hours_from_utc(lat, lon):
    tzwh = tzwhere.tzwhere()
    timezone_str = tzwh.tzNameAt(lat, lon)  # Seville coordinates

    timezone_now = pytz.timezone(timezone_str)
    utc_hours = datetime.datetime.now(timezone_now).utcoffset().total_seconds() / 60 / 60
    return utc_hours
