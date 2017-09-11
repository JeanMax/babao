"""Some utils functions for date handling"""

import pandas as pd


def to_datetime(df):
    """TODO"""

    df.index = pd.to_datetime(df.index, unit="ns")


def to_timestamp(df):
    """TODO"""

    df.index = df.index.view("int64")
