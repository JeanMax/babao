"""Some utils functions for date handling"""

import time
import pandas as pd


def to_datetime(df):
    """Convert the index of the given dataframe to datetime"""

    df.index = pd.to_datetime(df.index, unit="ns")


def to_timestamp(df):
    """Convert the index of the given dataframe to nanoseconds"""

    df.index = df.index.view("int64")


def nowMinus(years=0, weeks=0, days=0, hours=0, minutes=0, seconds=0):
    """Return the current timestamp (nanoseconds) minus the given parameters"""

    seconds += (
        minutes * 60
        + hours * 60 * 60
        + days * 60 * 60 * 24
        + weeks * 60 * 60 * 24 * 7
        + years * 60 * 60 * 24 * 7 * 365.25
    )

    return int(
        (time.time() - seconds) * 1e9
    )
