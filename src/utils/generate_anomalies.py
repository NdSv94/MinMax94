import numpy as np
import pandas as pd
from constants import MmxColumns


def generate_single_anomaly(df, index, col=MmxColumns.ROAD_TEMPERATURE):
    sign = np.random.choice([1, -1])
    series_adding = sign * np.random.uniform(2, 5)

    perturbated_series = df.loc[index, col] + series_adding
    return perturbated_series


def generate_short_term_anomaly(df, index, col=MmxColumns.ROAD_TEMPERATURE):
    series_duration = np.random.randint(3, 12)
    sign = np.random.choice([1, -1])

    series_adding = sign * np.random.exponential(2, series_duration)
    perturbation = np.cumsum(series_adding)

    perturbated_series = df.loc[index: (index + series_duration - 1), col] + perturbation
    return perturbated_series


def generate_long_term_anomaly(df, index, col=MmxColumns.ROAD_TEMPERATURE):
    series_duration = np.random.randint(300)
    multiplier = np.random.uniform(1.5, 2)
    perturbation = np.random.normal(0, 5, series_duration)

    perturbated_series = df.loc[index: (index + series_duration - 1), col] * multiplier + perturbation
    return perturbated_series
