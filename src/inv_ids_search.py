"""


To run:

$ python inv_ids_search.py --data_path=./data_csv/Raw/

--data_path - path to raw data

"""

# import of libraries

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import gc
import random
from os import listdir
from os.path import isfile, join
import pickle

import pandas as pd
# import ephem
import tensorflow as tf

from Filters import XGBFilter
from Preprocessing import Preprocessor

# getting file tree in directory "data_csv", which contains raw unfiltered data

mypath = './data_csv/Raw/'

flags = tf.flags

flags.DEFINE_string("data_path", None,
                    "Where the raw data is stored.")

FLAGS = flags.FLAGS


def main(_):
    if not FLAGS.data_path:
        raise ValueError("Must set --data_path to PTB data directory")

    dateparse = pd.to_datetime
    station_files = [f for f in listdir(mypath) if isfile(join(mypath, f)) if int(f.split('_', 1)[0])]
    station_files.sort()

    # reading loaded csv files from data_csv directory, output is a list (length=number of stations) of raw df
    raw_lmeteo_list = [pd.read_csv(mypath + '/' + station, index_col=0,
                                   dtype={'station_id': int, 'date_time': str},
                                   date_parser=dateparse, parse_dates=['date_time'])
                       for station in station_files[:6]]

    # fix problems with indexing, later this will be solved in loading part
    for elem in raw_lmeteo_list:
        elem.reset_index(drop=True, inplace=True)

    raw_data = pd.concat(raw_lmeteo_list)
    raw_data['id'] = random.sample(range(len(raw_data)), len(raw_data))
    raw_data['valid'] = True
    raw_data = raw_data.reset_index(drop=True)

    del raw_lmeteo_list
    gc.collect()

    # preprocessing of data

    preprocessor = Preprocessor()
    meteo_splitted = preprocessor.PivotTable(raw_data)
    del raw_data

    patterns_list = preprocessor.CreatePatternList(meteo_splitted)
    # del pivoted_df

    patterns_interpolated = preprocessor.InterpolatePatterns(patterns_list)
    del patterns_list

    patterns_lagged = preprocessor.CreateLaggedTable(patterns_interpolated)
    del patterns_interpolated

    final = pd.concat(patterns_lagged).reset_index(drop=True)


    #finding invalid data and creating dataset with them

    filt = XGBFilter(output='table')
    inv_ids = filt.verify(final)


    with open('invalid_ids.csv', 'w+') as f:
        inv_ids.to_csv(f)


    #
    # filt = XGBFilter(output='table')
    # inv_ids = filt.verify(final)
    #
    #
    # with open('invalid_ids.pkl', 'w+') as f:
    #     pickle.dump(inv_ids, f)


if __name__ == "__main__":
    tf.app.run()
