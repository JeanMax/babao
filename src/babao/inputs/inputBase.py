"""Base class for any input"""

from abc import ABC, abstractmethod
from typing import List

import pandas as pd

import babao.config as conf
import babao.utils.date as du
import babao.utils.file as fu
import babao.utils.log as log

INPUTS = []  # type: List[ABCInput]

LAST_WRITE = 0  # TODO: this is a stupid idea, bugs incoming!

REAL_TIME_LOOKBACK_DAYS = 7  # TODO: infere this from models/graph
CACHE_REAL_TIME_LOOKBACK_DAYS = REAL_TIME_LOOKBACK_DAYS * 4
TRAIN_TEST_RATIO = 3 / 4
SPLIT_DATE = int(
    du.EPOCH + (du.getTime(force=True) - du.EPOCH) * TRAIN_TEST_RATIO
)


def resampleSerie(s):
    """
    Call Serie.resample on s with preset parameters
    (the serie's index must be datetime)
    """
    # TODO: would be nice to do the base init once for all features
    # (ensure sync and save some computing)
    # also don't convert date or do it in utils.date
    base = du.toDatetime(LAST_WRITE)
    base = (base.minute + (base.second + 1) / 60) % 60
    return s.resample(
        str(conf.TIME_INTERVAL) + "Min",
        closed="right",
        label="right",
        base=base
    )


class ABCInput(ABC):
    """
    Base class for any input

    Your subclass should at least implement:
    * fetch : self -> DataFrame
    * raw_columns : List[str]


    And eventually: (if you want self.resample to works)
    * _resample : self -> DataFrame -> DataFrame
    * fillMissing : self -> DataFrame -> DataFrame
    * resampled_columns : List[str]

    (cf. specific method doc-string in this class)
    """

    @property
    @abstractmethod
    def raw_columns(self) -> List[str]:
        """
        The columns names of your raw data
        (as fetched and stored in database)
        """
        pass

    @property
    @abstractmethod
    def resampled_columns(self) -> List[str]:
        """The columns names of your resampled data (from raw data)"""
        pass

    def __init__(self):
        self.up_to_date = True
        self.current_row = None
        self._cache_data = None
        if conf.CURRENT_COMMAND == "train":
            self.cache()
        elif conf.CURRENT_COMMAND == "backtest":
            self.cache(since=SPLIT_DATE, till=du.getTime(force=True))
        else:  # real-time
            last_entry = fu.getLastRows(self.__class__.__name__, 1)
            if not last_entry.empty:
                du.setTime(last_entry.index[0])
            since = du.nowMinus(days=CACHE_REAL_TIME_LOOKBACK_DAYS)
            du.setTime(None)
            self.cache(since=since)

    def write(self, raw_data):
        """Write the given raw_data to the database, and cache it if needed"""
        if raw_data is None or raw_data.empty:
            return None
        if not fu.write(self.__class__.__name__, raw_data):
            log.warning(
                "Couldn't write to database frame '"
                + self.__class__.__name__ + "'"
            )
            return False
        self.cache(fresh_data=raw_data)
        return True

    def _readFromCache(self, since=None, till=None):
        """Read data in cache from ´since´ to ´till´"""
        if self._cache_data.empty:
            return self._cache_data
        return self._cache_data.loc[since:till]

    def _readFromFile(self, since=None, till=None):
        """Read data in database from ´since´ to ´till´"""
        where = None
        if since is not None:
            where = "index > %d" % since
        if till is not None:
            where += " & index < %d" % till
        return fu.read(self.__class__.__name__, where=where)

    def read(self, since=None, till=None):
        """Read data in database or cache from ´since´ to ´till´"""
        if since is None:
            since = du.EPOCH
        now = du.getTime()
        if till is None or till > now:
            till = now
        if self._cache_data is not None:
            return self._readFromCache(since, till)
        return self._readFromFile(since, till)

    def cache(self, fresh_data=None, since=None, till=None):
        """
        Save some data to cache

        If ´fresh_data´ is given, append it to cache,
        otherwise read in database from ´since´ to ´till´ and cache it
        """
        if fresh_data is not None:
            self._cache_data = self._cache_data.append(
                fresh_data
            )
            if not self._cache_data.empty:
                self._cache_data = self._cache_data.loc[
                    self._cache_data.index[-1]
                    - du.secToNano(CACHE_REAL_TIME_LOOKBACK_DAYS * 24 * 3600):
                ]
        else:
            log.debug(
                "Caching data from", du.toStr(since), "to", du.toStr(till),
                "(" + self.__class__.__name__ + ")"
            )
            self._cache_data = self._readFromFile(since, till)
        if not self._cache_data.empty:
            self.updateCurrentRow(self._cache_data.iloc[-1])
        else:
            log.warning("Database '" + self.__class__.__name__ + "' is emtpy")
            self._cache_data = pd.DataFrame(columns=self.raw_columns)

    def refreshCache(self):
        """Make sure the cache is up to date"""
        if self._cache_data.empty:
            since = None
        else:
            since = self._cache_data.index[-1]
        fresh_data = self._readFromFile(since)
        if not fresh_data.empty:
            self.cache(fresh_data=fresh_data)

    def resample(self, raw_data):
        """
        Return the DataFrame ´raw_data´ as a continuous time-serie

        This is a wrapper around _resample and fillMissing
        """
        if raw_data.empty:
            return pd.DataFrame(columns=self.resampled_columns)
        du.toDatetime(raw_data)
        resampled_data = self._resample(raw_data)
        resampled_data = self.fillMissing(resampled_data)
        du.toTimestamp(raw_data)
        du.toTimestamp(resampled_data)
        return resampled_data

    def updateCurrentRow(self, current_row=None, timestamp=None):
        """Update the property self.current_row, useful for time travel"""
        global LAST_WRITE
        if timestamp is not None:  # time travel
            if "Ledger" in self.__class__.__name__:
                return  # we're going to the future
            current_row = self._readFromCache(
                since=timestamp,
                till=timestamp + du.secToNano(12 * 3600)
                # assuming there is at least one row per day?
            )
            if not current_row.empty:
                current_row = current_row.iloc[0]
        if not current_row.empty:
            self.current_row = current_row
            if timestamp is not None:  # time travel
                LAST_WRITE = current_row.name
            else:
                LAST_WRITE = max(LAST_WRITE, current_row.name)
        else:  # spammy
            log.warning(
                "Couldn't update current row for database  '"
                + self.__class__.__name__ + "'"
            )

    @abstractmethod
    def fetch(self):
        """
        Return a time-serie DataFrame fetched from the internets

        This data will be stored on database for later use (and eventual
        resampling).
        Data can be continuous.
        Index must be nanosecond timestamps.
        """
        raise NotImplementedError(
            "Your Input class '%s' should implement a 'fetch' method :/"
            % self.__class__.__name__
        )

    def _resample(self, raw_data):
        """
        Return the DataFrame ´raw_data´ as a continuous time-serie

        ´raw_data´ is a DataFrame with the same columns as the ones returned
        by ´fetch´.

        You should use the helper function ´resampleSerie´ on the desired
        columns of your discrete ´raw_data´ to generate continuous data.
        """
        raise NotImplementedError(
            "Your Input class '%s' should implement a '_resample' method :/"
            % self.__class__.__name__
        )

    def fillMissing(self, resampled_data):
        """
        Fill missing values (np.nan/np.inf) in ´resampled_data´
        """
        raise NotImplementedError(
            "Your Input class '%s' should implement a 'fillMissing' method :/"
            % self.__class__.__name__
        )
