"""Some utils functions for date handling"""

import time
import pandas as pd

EPOCH = pd.Timestamp("2017-01-01").value
NOW = None


def setTime(now):
    """TODO"""
    global NOW
    NOW = now


def getTime(force=False):
    """TODO"""
    if not force and NOW is not None:
        return NOW
    return secToNano(time.time())


def toDatetime(df):
    """Convert the index of the given dataframe to datetime
    TODO"""

    if isinstance(df, pd.DataFrame):
        df.index = pd.to_datetime(df.index, unit="ns")
        return df
    return pd.to_datetime(df, unit="ns")


def toTimestamp(df):
    """Convert the index of the given dataframe to nanoseconds
    TODO"""

    if isinstance(df, pd.DataFrame):
        df.index = df.index.view("int64")
        return df
    return df.value


def toStr(t):
    """TODO"""
    if not isinstance(t, pd.Timestamp):
        t = toDatetime(t)
    return t.strftime("%Y/%m/%d %H:%M:%S")


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
    return int(nano / 10**9)
