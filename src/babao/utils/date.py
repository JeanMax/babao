"""Some utils functions for date handling"""

import time
import pandas as pd

NOW = None


def setTime(now):
    """TODO"""
    global NOW
    NOW = now


def getTime():
    """TODO"""
    if NOW is not None:
        return NOW
    return secToNano(time.time())


def to_datetime(df):
    """Convert the index of the given dataframe to datetime"""

    df.index = pd.to_datetime(df.index, unit="ns")


def to_timestamp(df):
    """Convert the index of the given dataframe to nanoseconds"""

    df.index = df.index.view("int64")


def nowMinus(years=0, weeks=0, days=0, hours=0, minutes=0):
    """Return the current timestamp (nanoseconds) minus the given parameters"""

    seconds = (
        minutes * 60
        + hours * 60 * 60
        + days * 60 * 60 * 24
        + weeks * 60 * 60 * 24 * 7
        + years * 60 * 60 * 24 * 365.25
    )

    return getTime() - secToNano(seconds)


def secToNano(sec):
    """
    Convert seconds to nanoseconds
    Just trying to avoid float rounding...
    """
    if isinstance(sec, (float, int)):
        return int(sec * 1e6) * 1000
    return (sec * 1e6).astype(int) * 1000


def nanoToSec(nano):
    """Convert nanoseconds to seconds"""
    return nano / 10**9
