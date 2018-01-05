"""Some utils functions for date handling"""

import pandas as pd


def to_datetime(df):
    """Convert the index of the given dataframe to datetime"""

    df.index = pd.to_datetime(df.index, unit="ns")


def to_timestamp(df):
    """Convert the index of the given dataframe to nanoseconds"""

    df.index = df.index.view("int64")
