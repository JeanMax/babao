"""Some utils functions for date handling and time traveling"""

import time
import numpy as np
import pandas as pd

# TODO: no hardcode: min(inputs.first_row)?
EPOCH = pd.Timestamp("2017-06-27").value


class TimeTraveler():
    """Class handling time travel tricks"""
    def __init__(self):
        self.now = None

    def setTime(self, now):
        """
        Set time to the given ´now´ nanoseconds

        Used for time traveling purpose
        """
        if now is None:
            self.now = None
        else:
            self.now = int(now)

    def getTime(self, force=False):
        """
        Return the current time in nanoseconds

        Used for time traveling purpose, so this might be a date in the past
        matching the current simulation state, unless ´force´ is set to True.
        """
        if not force and self.now is not None:
            return self.now
        return secToNano(time.time())

    def nowMinus(
            self, years=0, weeks=0, days=0, hours=0, minutes=0
    ):  # pylint: disable=R0913
        """
        Return the current timestamp (nanoseconds) minus the given parameters

        This will take into account time traveling tricks.
        """

        seconds = (
            minutes * 60
            + hours * 60 * 60
            + days * 60 * 60 * 24
            + weeks * 60 * 60 * 24 * 7
            + years * 60 * 60 * 24 * 365.25
        )

        return self.getTime() - secToNano(seconds)


TIME_TRAVELER = TimeTraveler()


def toDatetime(df):
    """
    Convert the index of the given dataframe to datetime

    Also works directly on a dataframe index.
    """

    if isinstance(df, pd.DataFrame):
        df.index = pd.to_datetime(df.index, unit="ns")
        return df
    return pd.to_datetime(df, unit="ns")


def toTimestamp(df):
    """
    Convert the index of the given dataframe to nanoseconds

    Also works directly on a dataframe index.
    """

    if isinstance(df, pd.DataFrame):
        df.index = df.index.view("int64")
        return df
    return df.value


def toStr(t):
    """
    Return the string representation of timestamp

    ´t´ can be a nanoseconds timestamp, or a panda datetime object.
    """
    if t is None:
        return "None"
    if not isinstance(t, pd.Timestamp):
        t = toDatetime(t)
    return t.strftime("%Y/%m/%d %H:%M:%S")


def secToNano(sec):
    """
    Convert seconds to nanoseconds
    Just trying to avoid float rounding...
    """
    # pylint bug: https://github.com/PyCQA/pylint/issues/2140
    if isinstance(sec, (float, int, np.floating, np.integer)):  # noqa: E1101
        return int(sec * 1e6) * 1000
    return (sec * 1e6).astype(int) * 1000


def nanoToSec(nano):
    """Convert nanoseconds to seconds"""
    return int(nano / 10**9)
