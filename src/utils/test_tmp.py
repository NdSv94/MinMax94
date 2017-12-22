import pandas as pd
import numpy as np
from copy import deepcopy
import gc
from tqdm import tqdm_notebook
import sys
sys.path.append('/home/ndsviriden/MinMax94/src/utils')
from Preprocessing import Preprocessor
import warnings
warnings.filterwarnings('ignore')

# getting file tree in directory "data_csv", which contains raw unfiltered data
mypath = '/mnt/HARD/MinMax94/data/data_all/CSV/Raw_extended/113_raw.csv'

# reading loaded csv files from data_csv directory, output is a list (length=number of stations) of raw df
raw_lmeteo = pd.read_csv(mypath, parse_dates = ['date_time'])

preprocessor = Preprocessor()
useful_features = ['t_air', 't_road', 't_underroad', 'pressure', 'dampness', 'cloudiness']
raw_lmeteo = preprocessor.SelectFeatures(raw_lmeteo, useful_features)
lmeteo_pivot = preprocessor.PivotTable(raw_lmeteo)
lmeteo_pivot = preprocessor.FixPressureScale(lmeteo_pivot)
pattern_list = preprocessor.CreatePatternList(lmeteo_pivot)


z = [pattern.date_time.max() - pattern.date_time.min() for pattern in pattern_list]
print(max(z))




